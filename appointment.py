import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from datetime import datetime
import spacy

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

db=firestore.client()

def entity():

    nlp = spacy.load("en_core_web_sm")

    input_text = "Hello i am Rishabh"

    doc = nlp(input_text)

    entity = {ent.label_: ent.text for ent in doc.ents}
    return entity

def save_to_firebase(entities):
    try:
        # Reference to the Firestore collection (e.g., "users")
        doc_ref = db.collection("appointment").add({
            "name": entities.get("name"),
            "phone": entities.get("phone"),
            "email": entities.get("email"),
            "doctor_name": entities.get("doctor_name"),
            "appointment_date": entities.get("appointment_date"),
            "appointment_time": entities.get("appointment_time"),
            "hospital": entities.get("hospital")
        })
        print("Document added with ID:", doc_ref[1].id)
    except Exception as e:
        print("Error adding document:", e)



if __name__ == "__main__":
    entity = entity()
    current_date = datetime.now()
    date_str = current_date.strftime("%Y-%m-%d")
    time_str = current_date.strftime("%I:%M %p")

    entities={
        "name":str(entity["PERSON"]),
        "phone":999999999,
        "email":"rishabhamar1234@gmail.com",
        "doctor_name":"Raj Sharma",
        "appointment_date":date_str,
        "appointment_time":time_str,
        "hospital":"ABC Hospital",
}
    save_to_firebase(entities)