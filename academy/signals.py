from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LessonComment, LessonProgress, Notification, ForumReply, Enrollment
from django.urls import reverse

@receiver(post_save, sender=Enrollment)
def create_installments_on_enrollment(sender, instance, created, **kwargs):
    """
    Ensure installments are created when an enrollment is created or updated
    with a monthly payment plan.
    """
    if instance.selected_payment_plan == 'monthly':
        # Generate installments if they don't exist
        instance.generate_installments()

@receiver(post_save, sender=LessonComment)
def notify_comment_reply(sender, instance, created, **kwargs):
    if created and instance.parent:
        # Notify the user who wrote the parent comment
        parent_user = instance.parent.user
        if parent_user != instance.user:
            Notification.objects.create(
                user=parent_user,
                message=f"{instance.user.username} respondió a tu comentario en '{instance.lesson.title}'",
                link=reverse('academy:lesson_detail', args=[instance.lesson.id]) + "#comments-section",
                notification_type='reply'
            )

@receiver(post_save, sender=LessonProgress)
def notify_assignment_grade(sender, instance, created, **kwargs):
    if instance.lesson.lesson_type == 'assignment' and instance.score is not None:
        exists = Notification.objects.filter(
            user=instance.user,
            notification_type='grade',
            is_read=False,
            message__contains=instance.lesson.title
        ).exists()

        if not exists:
            Notification.objects.create(
                user=instance.user,
                message=f"Tu tarea en '{instance.lesson.title}' ha sido calificada: {instance.score}",
                link=reverse('academy:lesson_detail', args=[instance.lesson.id]),
                notification_type='grade'
            )

@receiver(post_save, sender=ForumReply)
def notify_forum_reply(sender, instance, created, **kwargs):
    if created:
        # Notify topic owner
        topic_owner = instance.topic.user
        if topic_owner != instance.user:
            Notification.objects.create(
                user=topic_owner,
                message=f"{instance.user.username} respondió a tu tema '{instance.topic.title}'",
                link=reverse('academy:forum_topic_detail', args=[instance.topic.id]),
                notification_type='reply'
            )
