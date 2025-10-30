from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models import db

# ==============================================================
# USER CORE MODEL
# ==============================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-one relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    ratings = db.relationship('UserRating', backref='user', uselist=False, cascade='all, delete-orphan')

    # Example for future relationships:
    # bids = db.relationship('Bid', backref='user', lazy=True)
    # wallet = db.relationship('Wallet', backref='user', uselist=False)

    # Password helpers
    def set_password(self, password):
        """Hashes and sets user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# ==============================================================
# USER PROFILE MODEL
# ==============================================================

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255), default='default-avatar.webp')

    # Location fields (Leaflet.js integration)
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float)   # from Leaflet.js click event
    longitude = db.Column(db.Float)  # from Leaflet.js click event

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserProfile of {self.user.username}>"

    def auto_update_location(self, lat, lon):
        """Auto-updates the user's address whenever latitude or longitude changes."""
        try:
            self.latitude = float(lat)
            self.longitude = float(lon)

            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {"lat": lat, "lon": lon, "format": "json"}
            headers = {"User-Agent": "UserProfileLocationUpdater/1.0"}

            response = requests.get(url, params=params, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.address = data.get("display_name", "")
            else:
                # Keep old address if lookup fails
                print(f"Reverse geocode failed: {response.status_code}")
        except Exception as e:
            print(f"Error updating location: {e}")

    def update_profile_picture(self, file):
        """Updates the user's profile picture."""
        import os
        from werkzeug.utils import secure_filename
        from PIL import Image
        import uuid

        try:
            # Create directory if it doesn't exist
            upload_folder = os.path.join('app', 'profile_pictures')
            os.makedirs(upload_folder, exist_ok=True)

            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(upload_folder, unique_filename)

            # Open and process image with Pillow
            img = Image.open(file)
            
            # Convert to WebP format
            webp_filename = os.path.splitext(unique_filename)[0] + '.webp'
            webp_path = os.path.join(upload_folder, webp_filename)

            # Resize if too large while maintaining aspect ratio
            if max(img.size) > 800:
                ratio = 800 / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Save as WebP with good quality
            img.save(webp_path, 'WEBP', quality=85)

            # Delete old profile picture if it exists and it's not the default
            if self.profile_picture != 'default-avatar.webp':
                old_path = os.path.join('app', 'static', 'uploads', 'profile_pictures', self.profile_picture)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Update database with new filename
            self.profile_picture = webp_filename
            return True

        except Exception as e:
            print(f"Error updating profile picture: {e}")
            return False

    def get_profile_picture_url(self):
        """Returns the URL for the profile picture."""
        if self.profile_picture:
            if self.profile_picture == 'default-avatar.webp':
                return f"/static/images/{self.profile_picture}"
            return f"/static/uploads/profile_pictures/{self.profile_picture}"
        return "/static/images/default-avatar.webp"

# ==============================================================
# USER PREFERENCES MODEL
# ==============================================================

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Boolean alert preferences
    bidding_alerts = db.Column(db.Boolean, default=True)
    bid_listing = db.Column(db.Boolean, default=True)
    purchase_alert = db.Column(db.Boolean, default=True)
    post_alert = db.Column(db.Boolean, default=True)
    follow_alert = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserPreference of {self.user.username}>"


# ==============================================================
# USER RATING & PERFORMANCE MODEL
# ==============================================================

class UserRating(db.Model):
    __tablename__ = 'user_ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    rating = db.Column(db.Float, default=0.0)             # overall average (0–5)
    success_score = db.Column(db.Float, default=0.0)       # success percentage
    response_rate = db.Column(db.Float, default=0.0)       # responsiveness percentage
    successful_supply = db.Column(db.Integer, default=0)   # count of successful deliveries

    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserRating of {self.user.username}>"
