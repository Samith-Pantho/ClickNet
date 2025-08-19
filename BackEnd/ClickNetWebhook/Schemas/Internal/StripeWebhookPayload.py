from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Address(BaseModel):
    city: Optional[str]
    country: Optional[str]
    line1: Optional[str]
    line2: Optional[str]
    postal_code: Optional[str]
    state: Optional[str]

class CustomerDetails(BaseModel):
    address: Optional[Address]
    email: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    tax_exempt: Optional[str]
    tax_ids: Optional[List[Any]] = []

class TotalDetails(BaseModel):
    amount_discount: Optional[int]
    amount_shipping: Optional[int]
    amount_tax: Optional[int]

class CheckoutSession(BaseModel):
    id: str
    object: str
    amount_subtotal: Optional[int]
    amount_total: Optional[int]
    currency: Optional[str]
    customer_details: Optional[CustomerDetails]
    payment_intent: Optional[str]
    payment_status: Optional[str]
    status: Optional[str]
    mode: Optional[str]
    total_details: Optional[TotalDetails]
    # Add any other fields you might need
    # For example:
    # success_url: Optional[str]
    # cancel_url: Optional[str]

class EventData(BaseModel):
    object: CheckoutSession

class StripeWebhookPayload(BaseModel):
    id: Optional[str]
    object: str
    api_version: Optional[str]
    created: Optional[int]
    type: Optional[str]
    data: EventData
