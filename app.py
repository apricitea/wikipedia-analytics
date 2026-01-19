from flask import Blueprint, render_template

# Create a blueprint for the about section to keep the code modular.
# This allows for better organization as the application grows.
about_bp = Blueprint('about', __name__)

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