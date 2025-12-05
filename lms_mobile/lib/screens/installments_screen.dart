import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class InstallmentsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(color: Colors.white),
        title: Text("Mis Pagos", style: TextStyle(color: Colors.white)),
      ),
      body: FutureBuilder<List<dynamic>>(
        future: ApiService.getInstallments(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return Center(child: CircularProgressIndicator());
          final payments = snapshot.data!;
          if (payments.isEmpty) return Center(child: Text("No hay pagos pendientes", style: TextStyle(color: Colors.white54)));

          return ListView.builder(
            padding: EdgeInsets.all(20),
            itemCount: payments.length,
            itemBuilder: (context, index) {
              final p = payments[index];
              Color statusColor = Colors.orange;
              if (p['status'] == 'paid') statusColor = Colors.green;
              if (p['status'] == 'review') statusColor = Colors.blue;

              return Container(
                margin: EdgeInsets.only(bottom: 15),
                decoration: BoxDecoration(
                  color: Color(0xFF151E32),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: ListTile(
                  title: Text("Cuota #${p['installment_number']}", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  subtitle: Text("Vencimiento: ${p['due_date']}", style: TextStyle(color: Colors.white54)),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text("S/ ${p['amount']}", style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                      Text(p['status'].toUpperCase(), style: TextStyle(color: statusColor, fontSize: 10)),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
