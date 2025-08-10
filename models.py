# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Hero(db.Model):
    __tablename__ = 'heroes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    supername = db.Column(db.String, nullable=False)

    # Relationship to hero_powers
    hero_powers = db.relationship(
        'HeroPower',
        back_populates='hero',
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Basic hero info"""
        return {
            "id": self.id,
            "name": self.name,
            "super_name": self.supername
        }

    def to_dict_with_powers(self):
        """Hero info with powers list"""
        return {
            **self.to_dict(),
            "hero_powers": [hp.to_dict_with_power() for hp in self.hero_powers]
        }


class Power(db.Model):
    __tablename__ = 'powers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    hero_powers = db.relationship(
        'HeroPower',
        back_populates='power',
        cascade="all, delete-orphan"
    )

    @validates('description')
    def validate_description(self, key, value):
        """Ensure description is present and >= 20 chars"""
        if not value or len(value.strip()) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class HeroPower(db.Model):
    __tablename__ = 'hero_powers'
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id', ondelete='CASCADE'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id', ondelete='CASCADE'))

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    @validates('strength')
    def validate_strength(self, key, value):
        allowed = ['Strong', 'Weak', 'Average']
        if value not in allowed:
            raise ValueError(f"Strength must be one of {allowed}")
        return value

    def to_dict_with_power(self):
        """For nested hero_powers in hero detail"""
        return {
            "id": self.id,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
            "strength": self.strength,
            "power": self.power.to_dict() if self.power else None
        }

    def to_dict_full(self):
        """For POST /hero_powers return format"""
        return {
            "id": self.id,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
            "strength": self.strength,
            "hero": self.hero.to_dict() if self.hero else None,
            "power": self.power.to_dict() if self.power else None
        }
