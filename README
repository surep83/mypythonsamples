Key Features:

Secure API Key Management:
The script uses the python-dotenv package to load the Google API key from a .env file, keeping sensitive credentials out of the source code and version control.

Location-Based Search:
It searches for places matching the keyword "dance classes" within a 10-kilometer radius of a specified latitude and longitude (in this case, 12.849455,80.141448). The Google Places Nearby Search API is used to retrieve relevant results.

Distance Calculation:
For each place found, the script calculates the distance from the origin point using the Haversine formula. This formula computes the great-circle distance between two points on the Earth based on their latitude and longitude, providing an accurate measurement in kilometers.

Data Organization:
The script collects key details for each place, including the name, address, rating, number of user ratings, and calculated distance in kilometers. These details are stored in a pandas DataFrame for easy manipulation and sorting.

Sorting and Export:
Results are sorted by distance, from nearest to farthest, ensuring that the most accessible options appear first. The sorted data is then exported to an Excel file (dance_classes_nearby.xlsx), making it easy to share or further analyze.

Usage:
To use the script, ensure you have a valid Google Places API key stored in a .env file as GOOGLE_API_KEY. Install the required Python packages (requests, pandas, python-dotenv) and run the script. The output Excel file will contain a list of dance classes near your specified location, sorted by proximity.

This approach streamlines local business discovery and can be adapted for other types of searches by changing the keyword or location.
