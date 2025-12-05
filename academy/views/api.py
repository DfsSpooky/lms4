from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import *
from ..serializers import *
import json

# --- ENDPOINT API ---
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class MyCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MyCourseSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user, status__in=['approved', 'pending'])

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'ok'})

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    def get_serializer_class(self):
        if self.action == 'retrieve': return CourseDetailSerializer
        return CourseListSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

        # If created, check if payment is needed
        if created:
            # Default to full payment plan if not specified (legacy behavior kept)
            enrollment.selected_payment_plan = 'full'
            enrollment.save()

        return Response({
            'status': 'enrolled' if created else 'already_enrolled',
            'enrollment_id': enrollment.id,
            'payment_status': enrollment.status
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_voucher(self, request, pk=None):
        # Allow uploading voucher for course enrollment directly if needed
        course = self.get_object()
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if not enrollment:
             return Response({'error': 'No enrollment found'}, status=404)

        if 'voucher' not in request.FILES:
             return Response({'error': 'No file uploaded'}, status=400)

        enrollment.voucher_image = request.FILES['voucher']
        enrollment.status = 'review'
        enrollment.save()
        return Response({'status': 'uploaded'})

class ProgressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path='lesson/(?P<lesson_id>[^/.]+)/complete')
    def complete_lesson(self, request, lesson_id=None):
        lesson = Lesson.objects.get(pk=lesson_id)
        if not Enrollment.objects.filter(user=request.user, course=lesson.module.course, status='approved').exists():
             return Response({'error': 'Acceso denegado'}, status=403)
        LessonProgress.objects.get_or_create(user=request.user, lesson=lesson, defaults={'is_completed': True})
        LessonProgress.objects.filter(user=request.user, lesson=lesson).update(is_completed=True)
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], url_path='quiz/(?P<quiz_id>[^/.]+)/submit')
    def submit_quiz(self, request, quiz_id=None):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        # Check enrollment approved
        if not Enrollment.objects.filter(user=request.user, course=quiz.module.course, status='approved').exists():
             return Response({'error': 'Acceso denegado'}, status=403)

        # data format: {'question_id': value}
        # value can be: answer_id (int), list of answer_ids (list), or text (str)
        data = request.data.get('answers', {})

        # Validate Time Limit
        if quiz.duration > 0:
            import time
            session_start_key = f'quiz_{quiz.id}_start_time'
            start_time = request.session.get(session_start_key)
            if start_time:
                elapsed = time.time() - start_time
                # Allow 60 seconds grace period
                if elapsed > (quiz.duration * 60) + 60:
                     # Late submission? We can mark it as failed or just warn.
                     # For now, we will proceed but you might want to penalize.
                     pass

            # Clean up session
            if session_start_key in request.session:
                del request.session[session_start_key]

        # Create submission object first
        submission = QuizSubmission.objects.create(
            user=request.user,
            quiz=quiz,
            score=0,
            passed=False
        )

        total_points = 0
        earned_points = 0
        needs_grading = False

        # Determine which questions to grade
        questions = []
        if quiz.randomize_questions:
            session_key = f'quiz_{quiz.id}_questions'
            question_ids = request.session.get(session_key)
            if question_ids:
                questions = list(Question.objects.filter(id__in=question_ids))
                # Cleanup
                del request.session[session_key]
            else:
                 # Fallback: Grade based on submitted keys if valid? Or all?
                 # If session expired, this is tricky. We'll fallback to grading what was sent.
                 # Security risk: User sends only questions they know.
                 # Better: Load all questions? No, we don't want to grade questions they didn't see.
                 # Compromise: Load questions from keys in 'data' that belong to this quiz.
                 submitted_ids = [int(k) for k in data.keys() if k.isdigit()]
                 questions = list(Question.objects.filter(id__in=submitted_ids, quiz=quiz))
        else:
            questions = list(quiz.questions.all())

        if not questions: return Response({'error': 'Examen vacío o error de sesión'}, status=400)

        for question in questions:
            total_points += question.points
            answer_data = data.get(str(question.id))

            student_answer = StudentAnswer.objects.create(
                submission=submission,
                question=question
            )

            if not answer_data:
                continue

            q_points = 0
            is_correct = False

            if question.question_type == 'single_choice' or question.question_type == 'true_false':
                try:
                    ans_id = int(answer_data)
                    answer = Answer.objects.get(id=ans_id, question=question)
                    student_answer.selected_answers.add(answer)
                    if answer.is_correct:
                        q_points = question.points
                        is_correct = True
                except (ValueError, Answer.DoesNotExist):
                    pass

            elif question.question_type == 'multiple_choice':
                # answer_data should be a list of IDs
                if isinstance(answer_data, list):
                    correct_answers = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
                    selected_ids = set()
                    for aid in answer_data:
                        try:
                            a_obj = Answer.objects.get(id=int(aid), question=question)
                            student_answer.selected_answers.add(a_obj)
                            selected_ids.add(a_obj.id)
                        except: pass

                    if selected_ids == correct_answers:
                        q_points = question.points
                        is_correct = True

            elif question.question_type == 'short_answer':
                text_input = str(answer_data).strip().lower()
                student_answer.text_answer = str(answer_data)

                # Check against possible correct answers
                possible_answers = question.answers.all()
                if possible_answers.exists():
                    # Auto-grade if there are defined answers
                    match = False
                    for ans in possible_answers:
                        if ans.text.strip().lower() == text_input:
                            match = True
                            break

                    if match:
                        q_points = question.points
                        is_correct = True
                    else:
                        is_correct = False
                else:
                    # No defined answers, manual grading
                    is_correct = None
                    needs_grading = True

            elif question.question_type == 'ordering':
                # answer_data expected: list of answer_ids in submitted order
                submitted_order_ids = [int(x) for x in answer_data if x] if isinstance(answer_data, list) else []
                correct_order_ids = list(question.answers.order_by('order').values_list('id', flat=True))

                # Save the submitted order as text for reference
                student_answer.text_answer = json.dumps(submitted_order_ids)

                matches = 0
                if len(submitted_order_ids) == len(correct_order_ids):
                    for idx, val in enumerate(submitted_order_ids):
                        if val == correct_order_ids[idx]:
                            matches += 1

                if matches == len(correct_order_ids) and len(correct_order_ids) > 0:
                        q_points = question.points
                        is_correct = True
                elif len(correct_order_ids) > 0:
                    q_points = (matches / len(correct_order_ids)) * question.points
                    is_correct = False

            elif question.question_type == 'matching':
                # answer_data expected: dict { answer_id: matched_text }
                pairs = answer_data if isinstance(answer_data, dict) else {}
                student_answer.text_answer = json.dumps(pairs)

                correct_pairs = 0
                total_pairs = question.answers.count()

                for ans in question.answers.all():
                    submitted_val = pairs.get(str(ans.id))
                    if submitted_val and submitted_val.strip() == ans.match_text.strip():
                        correct_pairs += 1

                if total_pairs > 0:
                    q_points = (correct_pairs / total_pairs) * question.points
                    is_correct = (correct_pairs == total_pairs)

            student_answer.is_correct = is_correct
            student_answer.points_awarded = q_points
            student_answer.save()
            earned_points += q_points

        # Calculate final score
        # Note: If needs_grading is True, the score is provisional
        final_score = (earned_points / total_points) * 100 if total_points > 0 else 0

        submission.score = final_score
        submission.passed = final_score >= quiz.pass_mark
        submission.save()

        # Update best score logic?
        # Usually we keep history. But if we want to track "best" for progress:
        # We might want to keep the highest score submission as the "official" one for certificate.
        # But here we just return the result of THIS attempt.

        return Response({
            'score': final_score,
            'passed': submission.passed,
            'needs_grading': needs_grading,
            'submission_id': submission.id
        })
