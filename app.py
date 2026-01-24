from flask import Blueprint, jsonify, render_template

# Create a blueprint for FAQ related routes.
# This allows for better organization of the codebase.
faq_bp = Blueprint('faq', __name__)

# Create a blueprint for the about section to keep the code modular.
# This allows for better organization as the application grows.
about_bp = Blueprint('about', __name__)

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


@about_bp.route('/about')
def about():
    """
    Route handler for the '/about' page.

    This function performs the following actions:
    1. Imports team member data (simulated here as a list of dictionaries).
    2. Passes this data to the 'about.html' template for rendering.

    Returns:
        str: The rendered HTML content for the about page.
    """
    # Importing team data.
    # In a production environment, this might come from a database,
    # a JSON file, or a configuration module.
    team_data = [
        {
            "name": "Alice Johnson",
            "role": "Lead Developer",
            "bio": "Alice is a seasoned developer with a passion for clean architecture."
        },
        {
            "name": "Bob Smith",
            "role": "Product Manager",
            "bio": "Bob ensures the product meets user needs and business goals."
        },
        {
            "name": "Charlie Davis",
            "role": "Designer",
            "bio": "Charlie creates intuitive and visually stunning user interfaces."
        }
    ]

    # Render the template, passing the team_data to the context.
    # The template can iterate over this variable to display team members.
    return render_template('about.html', team=team_data)
