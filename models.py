from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Hero(db.Model):
    __tablename__ = 'heroes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    supername = db.Column(db.String)


    def to_dict(self):
        return{
            "id": self.id,
            "name":self.name,
            "supername":self.supername
        }
    
    def to_dict_with_powers(self):
        return {
            **self.to_dict(),
            "hero_powers": [hp.to_dict_with_power() for hp in self.hero_powers],
        }



class Power(db.Model):
    __tablename__ = 'powers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String(20))  # Will validate length elsewhere


    def to_dict(self):
        return{
            "id":self.id,
            "name": self.name,
            "description":self.description
        }


class HeroPower(db.Model):
    __tablename__ = 'hero_powers'
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)  # Field to validate
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id', ondelete='CASCADE'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id', ondelete='CASCADE'))

    hero = db.relationship('Hero', backref='hero_powers', cascade="all, delete-orphan")
    power = db.relationship('Power', backref='hero_powers', cascade="all, delete-orphan")

    @validates('strength')
    def validate_strength(self, key, value):
        allowed_values = ['Strong', 'Weak', 'Average']
        if value not in allowed_values:
            raise ValueError(f"Strength must be one of {allowed_values}")
        return value
