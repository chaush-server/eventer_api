from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import backref

from apps.models import ProviderEnum, ValidateStatusEnum, StatusEnum, TicketTypeEnum
from extensions import db


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(255), nullable=False)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(255), nullable=False)
    lastName = db.Column(db.String(255), nullable=False)
    middleName = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.DateTime)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    trusted = db.Column(db.Boolean, default=False)
    provider = db.Column(db.Enum(ProviderEnum), default="SYSTEM")
    roleId = db.Column(db.Integer, ForeignKey('role.id'), default=1, nullable=False)


class Organizer(db.Model):
    __tablename__ = 'organizer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.String(255), nullable=False)
    background = db.Column(db.String(255))
    description = db.Column(db.Text)
    cardNumber = db.Column(db.String(255), nullable=False)
    cardHolderName = db.Column(db.String(255), nullable=False)
    facebook = db.Column(db.String(255))
    telegram = db.Column(db.String(255))
    vk = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    instagram = db.Column(db.String(255))

    userId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=backref("organizers", cascade="all,delete"))


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    expectedAmount = db.Column(db.Numeric(10, 2), nullable=False)
    recommendedDonation = db.Column(db.Numeric(10, 2), nullable=False)

    validateStatus = db.Column(db.Enum(ValidateStatusEnum), nullable=False)
    countOfMembers = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(StatusEnum), nullable=False)
    concession = db.Column(db.String(255), nullable=False)

    genreId = db.Column(db.Integer, ForeignKey('genre.id'), nullable=False)

    organizerId = db.Column(db.Integer, ForeignKey('organizer.id'), nullable=False)
    organizer = db.relationship('Organizer', backref=backref("events", cascade="all,delete"))


class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    dateTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    ticketType = db.Column(db.Enum(TicketTypeEnum), nullable=False)
    seat = db.Column(db.Integer, nullable=False)

    eventDatesId = db.Column(db.Integer, ForeignKey('eventDates.id', ondelete='CASCADE'), nullable=False)
    eventDates = db.relationship('EventDates', backref=backref("tickets", cascade="all,delete"))

    bookingId = db.Column(db.Integer, ForeignKey('booking.id'), nullable=False)
    booking = db.relationship('Booking', backref=backref("tickets", cascade="all,delete"))


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photos = db.Column(ARRAY(db.Text), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    seats = db.Column(db.Integer, nullable=False)

    countryId = db.Column(db.Integer, ForeignKey('country.id'), nullable=False)
    country = db.relationship('Country', backref=backref("venues", cascade="all,delete"))

    stateId = db.Column(db.Integer, ForeignKey('state.id'), nullable=False)
    state = db.relationship('State', backref=backref("venues", cascade="all,delete"))

    cityId = db.Column(db.Integer, ForeignKey('city.id'), nullable=False)
    city = db.relationship('City', backref=backref("venues", cascade="all,delete"))

    eventId = db.Column(db.Integer, ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=backref("venues", cascade="all,delete"))


class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    countryId = db.Column(db.Integer, ForeignKey('country.id'), nullable=False)
    country = db.relationship('Country', backref='states')


class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    stateId = db.Column(db.Integer, ForeignKey('state.id'), nullable=False)
    state = db.relationship('State', backref='cities')


class EventDates(db.Model):
    __tablename__ = 'eventDates'

    id = db.Column(db.Integer, primary_key=True)
    startDateTime = db.Column(db.DateTime, nullable=False)
    endDateTime = db.Column(db.DateTime, nullable=False)

    eventId = db.Column(db.Integer, ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=backref("eventDates", cascade="all,delete"))


class EventDonation(db.Model):
    __tablename__ = 'eventDonation'

    id = db.Column(db.Integer, primary_key=True)
    dateTime = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    comment = db.Column(db.String(255))

    userId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=backref("eventDonations", cascade="all,delete"))

    eventId = db.Column(db.Integer, ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=backref("eventDonations", cascade="all,delete"))


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)

    eventId = db.Column(db.Integer, ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=backref("booking", cascade="all,delete"), uselist=False)

    userId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=backref("bookings", cascade="all,delete"))


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    genres = db.relationship('Genre', backref='category')


class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    categoryId = db.Column(db.Integer, ForeignKey('category.id'), nullable=False)
    events = db.relationship('Event', backref='genre')


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    rate = db.Column(db.Integer, nullable=False)
    dateTime = db.Column(db.DateTime, nullable=False)
    photos = db.Column(ARRAY(db.Text))

    eventId = db.Column(db.Integer, ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=backref("feedbacks", cascade="all,delete"))

    userId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=backref("feedbacks", cascade="all,delete"))


class FavouriteOrganizer(db.Model):
    __tablename__ = 'favouriteOrganizer'

    id = db.Column(db.Integer, primary_key=True)
    dateTime = db.Column(db.DateTime, nullable=False)

    userId = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=backref("favouriteOrganizers", cascade="all,delete"))

    organizerId = db.Column(db.Integer, ForeignKey('organizer.id'), nullable=False)
    organizer = db.relationship('Organizer', backref=backref("favouriteOrganizers", cascade="all,delete"))
