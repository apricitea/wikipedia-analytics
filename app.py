from flask import Blueprint, jsonify, render_template

# Create a blueprint for FAQ related routes. 
# This allows for better organization of the codebase.
faq_bp = Blueprint('faq', __name__)

# Predefined Q&A items as requested.
# In a production environment, these might be stored in a database.
FAQ_ITEMS = [
    {
        "id": 1,
        "question": "How do I reset my password?",
        "answer": "Go to Settings > Security and click on 'Reset Password'. You will receive an email with instructions."
    },
    {
        "id": 2,
        "question": "What payment methods do you accept?",
        "answer": "We accept all major credit cards (Visa, Mastercard, American Express) and PayPal."
    },
    {
        "id": 3,
        "question": "How can I contact customer support?",
        "answer": "You can reach our support team via email at support@example.com or through the contact form on our website."
    },
    {
        "id": 4,
        "question": "Is there a mobile app available?",
        "answer": "Yes, our mobile app is available for both iOS and Android devices. You can download it from the App Store or Google Play."
    },
    {
        "id": 5,
        "question": "How do I delete my account?",
        "answer": "To delete your account, please navigate to Settings > Account > Delete Account. Please note that this action is irreversible."
    }
]

@faq_bp.route('/faq')
def get_faq():
    """
    Handles the GET request for the FAQ endpoint.
    
    Returns:
        JSON: A list containing the 5 predefined Q&A items.
    """
    try:
        # Return the data as JSON with a 200 OK status code
        return jsonify({
            "status": "success",
            "count": len(FAQ_ITEMS),
            "data": FAQ_ITEMS
        }), 200
    except Exception as e:
        # Log the error in a real application
        # app.logger.error(f"Error serving FAQ: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred while fetching FAQs."
        }), 500