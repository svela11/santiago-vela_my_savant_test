#!/usr/bin/env python3
"""
Servidor Mock API para el sistema de logística WAT Framework.
Sirve datos de envíos desde archivo JSON y maneja operaciones CRUD.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Modelos Pydantic
class ShipmentStatus(BaseModel):
    shipment_id: str
    status: str
    origin: str
    destination: str
    pickup_date: str
    delivery_date: str
    estimated_delivery: str
    weight: str
    pieces: str
    customer_code: str
    driver_reference: str

class RescheduleRequest(BaseModel):
    new_date: str = Field(..., description="Nueva fecha en formato YYYY-MM-DD")
    new_time: str = Field(..., description="Nueva hora en formato HH:MM")
    reason: str = Field(..., description="Motivo de la reprogramación")

class TicketRequest(BaseModel):
    shipment_id: str
    issue_type: str = Field(..., description="Tipo de incidencia: daño, retraso, pérdida, otro")
    description: str
    severity: str = Field(default="medium", description="Severidad: low, medium, high")
    contact_info: str

class MockAPIServer:
    def __init__(self):
        self.app = FastAPI(
            title="Logistics Mock API",
            description="API Mock para sistema de logística",
            version="1.0.0"
        )
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.shipments_data = {}
        self.tickets_data = []
        self.load_shipments_data()
        self.setup_routes()
    
    def load_shipments_data(self):
        """Cargar datos de envíos desde el archivo JSON."""
        json_file = Path("Listado Ordenes.json")
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Procesar y estructurar los datos
            for item in raw_data:
                shipment_id = item.get('shipmentid', '')
                if shipment_id:
                    fax_data = item.get('fax', {})
                    
                    # Determinar estado basado en fechas
                    status = self._determine_status(fax_data)
                    
                    self.shipments_data[shipment_id] = {
                        'shipment_id': shipment_id,
                        'status': status,
                        'order_type': fax_data.get('order_type', ''),
                        'customer_code': fax_data.get('customer_code', ''),
                        'origin': f"{fax_data.get('stop1_name', '')} - {fax_data.get('stop1_city', '')}, {fax_data.get('stop1_st', '')}",
                        'destination': f"{fax_data.get('stop2_name', '')} - {fax_data.get('stop2_city', '')}, {fax_data.get('stop2_st', '')}",
                        'pickup_date': fax_data.get('date1', ''),
                        'delivery_date': fax_data.get('date2', ''),
                        'pickup_time': fax_data.get('time1', ''),
                        'delivery_time': fax_data.get('time2', ''),
                        'weight': fax_data.get('weight', ''),
                        'pieces': fax_data.get('pieces', ''),
                        'rate': fax_data.get('rate', ''),
                        'fuel_surcharge': fax_data.get('fuelsurcharge', ''),
                        'container_info': f"{fax_data.get('container_letters', '')} {fax_data.get('container_numbers', '')}".strip(),
                        'driver_reference': fax_data.get('fordriver', ''),
                        'seal': fax_data.get('seal', ''),
                        'bol': fax_data.get('BOL', ''),
                        'created_at': item.get('hour_init', ''),
                        'updated_at': item.get('hour_end', '')
                    }
        
        print(f"Cargados {len(self.shipments_data)} envíos")
    
    def _determine_status(self, fax_data: Dict) -> str:
        """Determinar estado del envío basado en fechas."""
        pickup_date = fax_data.get('date1', '')
        delivery_date = fax_data.get('date2', '')
        
        if not pickup_date:
            return "pendiente"
        
        try:
            pickup_dt = datetime.strptime(pickup_date, '%Y-%m-%d')
            today = datetime.now()
            
            if pickup_dt > today:
                return "programado"
            elif pickup_dt <= today and (not delivery_date or delivery_date == ""):
                return "en_transito"
            elif delivery_date:
                delivery_dt = datetime.strptime(delivery_date, '%Y-%m-%d')
                if delivery_dt <= today:
                    return "entregado"
                else:
                    return "en_transito"
            else:
                return "en_transito"
        except:
            return "pendiente"
    
    def setup_routes(self):
        """Configurar rutas de la API."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "ok", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/shipments/{shipment_id}")
        async def get_shipment(shipment_id: str):
            """Obtener información de un envío específico."""
            if shipment_id not in self.shipments_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Envío {shipment_id} no encontrado"
                )
            
            shipment = self.shipments_data[shipment_id]
            
            # Calcular ETA si está en tránsito
            eta = self._calculate_eta(shipment)
            
            return {
                "shipment_id": shipment['shipment_id'],
                "status": shipment['status'],
                "origin": shipment['origin'],
                "destination": shipment['destination'],
                "pickup_date": shipment['pickup_date'],
                "delivery_date": shipment['delivery_date'],
                "pickup_time": shipment['pickup_time'],
                "delivery_time": shipment['delivery_time'],
                "estimated_delivery": eta,
                "weight": shipment['weight'],
                "pieces": shipment['pieces'],
                "customer_code": shipment['customer_code'],
                "driver_reference": shipment['driver_reference'],
                "container_info": shipment['container_info'],
                "rate": shipment['rate'],
                "fuel_surcharge": shipment['fuel_surcharge'],
                "order_type": shipment['order_type']
            }
        
        @self.app.post("/shipments/{shipment_id}/reschedule")
        async def reschedule_shipment(shipment_id: str, request: RescheduleRequest):
            """Reprogramar entrega de un envío."""
            if shipment_id not in self.shipments_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Envío {shipment_id} no encontrado"
                )
            
            shipment = self.shipments_data[shipment_id]
            
            # Validar que el envío se puede reprogramar
            if shipment['status'] in ['entregado', 'cancelado']:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede reprogramar un envío con estado: {shipment['status']}"
                )
            
            # Validar fecha
            try:
                new_datetime = datetime.strptime(f"{request.new_date} {request.new_time}", '%Y-%m-%d %H:%M')
                if new_datetime <= datetime.now():
                    raise HTTPException(
                        status_code=400,
                        detail="La nueva fecha debe ser futura"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de fecha/hora inválido. Use YYYY-MM-DD y HH:MM"
                )
            
            # Actualizar envío
            old_date = shipment['delivery_date']
            old_time = shipment['delivery_time']
            
            shipment['delivery_date'] = request.new_date
            shipment['delivery_time'] = request.new_time
            shipment['updated_at'] = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "Entrega reprogramada exitosamente",
                "shipment_id": shipment_id,
                "old_delivery": f"{old_date} {old_time}",
                "new_delivery": f"{request.new_date} {request.new_time}",
                "reason": request.reason,
                "updated_at": shipment['updated_at']
            }
        
        @self.app.post("/tickets")
        async def create_ticket(request: TicketRequest):
            """Crear ticket de incidencia."""
            # Validar que el envío existe
            if request.shipment_id not in self.shipments_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Envío {request.shipment_id} no encontrado"
                )
            
            # Generar ID de ticket
            ticket_id = f"TK{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            ticket = {
                "ticket_id": ticket_id,
                "shipment_id": request.shipment_id,
                "issue_type": request.issue_type,
                "description": request.description,
                "severity": request.severity,
                "contact_info": request.contact_info,
                "status": "abierto",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.tickets_data.append(ticket)
            
            # Guardar tickets en archivo
            self._save_tickets()
            
            return {
                "success": True,
                "message": "Ticket creado exitosamente",
                "ticket_id": ticket_id,
                "estimated_response_time": "24 horas",
                "next_steps": "Un representante se contactará con usted dentro de las próximas 24 horas"
            }
        
        @self.app.get("/tickets/{ticket_id}")
        async def get_ticket(ticket_id: str):
            """Obtener información de un ticket."""
            ticket = next((t for t in self.tickets_data if t['ticket_id'] == ticket_id), None)
            if not ticket:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ticket {ticket_id} no encontrado"
                )
            return ticket
        
        @self.app.get("/shipments")
        async def list_shipments(limit: int = 10, customer_code: Optional[str] = None):
            """Listar envíos con filtros opcionales."""
            shipments = list(self.shipments_data.values())
            
            if customer_code:
                shipments = [s for s in shipments if s['customer_code'] == customer_code]
            
            return {
                "shipments": shipments[:limit],
                "total": len(shipments),
                "showing": min(limit, len(shipments))
            }
    
    def _calculate_eta(self, shipment: Dict) -> str:
        """Calcular tiempo estimado de llegada."""
        if shipment['status'] == 'entregado':
            return shipment['delivery_date']
        
        if shipment['delivery_date']:
            return shipment['delivery_date']
        
        # Estimar basado en fecha de pickup + 2-3 días
        try:
            pickup_date = datetime.strptime(shipment['pickup_date'], '%Y-%m-%d')
            eta = pickup_date + timedelta(days=2)
            return eta.strftime('%Y-%m-%d')
        except:
            return "Por determinar"
    
    def _save_tickets(self):
        """Guardar tickets en archivo JSON."""
        tickets_file = Path("data/tickets.json")
        tickets_file.parent.mkdir(exist_ok=True)
        
        with open(tickets_file, 'w', encoding='utf-8') as f:
            json.dump(self.tickets_data, f, indent=2, ensure_ascii=False)

def main():
    """Ejecutar servidor API."""
    server = MockAPIServer()
    
    print("🚀 Iniciando servidor Mock API...")
    print("📋 Documentación disponible en: http://localhost:8000/docs")
    print("🔍 Health check en: http://localhost:8000/health")
    
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

# Crear instancia global para uvicorn
server_instance = MockAPIServer()
app = server_instance.app

if __name__ == "__main__":
    main()
