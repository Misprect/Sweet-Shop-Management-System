// src/types/Sweet.ts
export interface Sweet {
    id: number;
    name: string;
    description: string;
    price: number;
    owner_id: number; // Important for Pydantic/FastAPI communication
}
