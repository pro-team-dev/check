import os
import random
import datetime
import base64
from django.core.management.base import BaseCommand
from travelagency.models import TravelAgency, Tour, Gallery
from PIL import Image

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        # Assuming the temp folder is in the same directory as populate_db.py
        temp_folder = os.path.join(os.path.dirname(__file__), '..', 'temp')

        # Create Travel Agencies
        travel_agencies = []
        for i in range(5):
            travel_agency = TravelAgency.objects.create(
                name=f'Travel Agency {i}',
                address=f'Address {i}',
                contact_num=random.randint(1000000000, 9999999999),
                website=f'http://www.travelagency{i}.com',
                profile=self.get_base64_encoded_image(temp_folder, random.choice(os.listdir(temp_folder))),
            )
            travel_agencies.append(travel_agency)

        # Create Tours
        for i in range(10):
            tour = Tour.objects.create(
                title=f'Tour {i}',
                description=f'Description for Tour {i}',
                price=random.uniform(100, 1000),
                duration_days=random.randint(1, 10),
                start_date=datetime.date.today() + datetime.timedelta(days=random.randint(1, 30)),
                end_date=datetime.date.today() + datetime.timedelta(days=random.randint(31, 60)),
                tour_type=random.choice(['hiking', 'trekking', 'nature', 'beach', 'city', 'cultural', 'wildlife', 'cruise']),
                travelagency=random.choice(travel_agencies),
            )

            # Create Galleries for each Tour
            for j in range(3):
                compressed_image = self.compress_image(temp_folder, random.choice(os.listdir(temp_folder)))
                if compressed_image is not None:
                    gallery = Gallery.objects.create(image=compressed_image)
                    tour.gallery.add(gallery)  # Add the gallery to the tour's many-to-many field
                    tour.save()  # Save the tour to persist the many-to-many relationship

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))

    def get_base64_encoded_image(self, folder, image_filename):
        image_path = os.path.join(folder, image_filename)
        with open(image_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_image

    def compress_image(self, folder, image_filename):
        image_path = os.path.join(folder, image_filename)

        try:
            # Open and compress the image using Pillow
            with Image.open(image_path) as img:
                compressed_image_path = os.path.join(folder, f'compressed_{image_filename}')
                img.save(compressed_image_path, quality=20)  # Adjust the quality as needed

                # Read the compressed image and return base64 encoding
                with open(compressed_image_path, 'rb') as compressed_image_file:
                    compressed_encoded_image = base64.b64encode(compressed_image_file.read()).decode('utf-8')

                # Remove the temporary compressed image file
                os.remove(compressed_image_path)

                return compressed_encoded_image

        except Exception as e:
            print(f"Error compressing image: {e}")
            return None
