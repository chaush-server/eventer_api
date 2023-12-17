from datetime import datetime
from werkzeug.security import generate_password_hash
from faker import Faker

from apps.models import ProviderEnum, ValidateStatusEnum, StatusEnum, TicketTypeEnum
from extensions import db
from apps.models.models import Role, User, Organizer, Event, Ticket, Venue, Country, State, City, EventDates, \
    EventDonation, Booking, Category, Genre, Feedback, FavouriteOrganizer


def mock_database():
    fake = Faker('ru_RU')

    def create_role():
        # Создаем роль
        role = Role(
            role='user'
        )

        # Сохраняем роль в базу данных
        db.session.add(role)
        db.session.commit()
        return role

    def create_user(email: str | None = None, password: str | None = None):
        # Создаем пользователя
        user = User(
            firstName=fake.first_name(),
            lastName=fake.last_name(),
            middleName=fake.middle_name(),
            birthday=fake.date_of_birth(),
            password=generate_password_hash(password),
            email=email,
            avatar=fake.image_url(),
            trusted=True,
            provider=ProviderEnum.SYSTEM,
        )

        # Сохраняем пользователя в базу данных
        db.session.add(user)
        db.session.commit()
        return user

    def create_organizer(user_id: int) -> Organizer:
        # Создаем организатора
        organizer = Organizer(
            name=fake.company(),
            logo=fake.image_url(),
            background=fake.image_url(),
            description=fake.text(),
            cardNumber=fake.credit_card_number(),
            cardHolderName=fake.name(),
            facebook=fake.url(),
            telegram=fake.url(),
            vk=fake.url(),
            twitter=fake.url(),
            instagram=fake.url(),

            userId=user_id
        )

        # Сохраняем организатора в базу данных
        db.session.add(organizer)
        db.session.commit()
        return organizer

    def create_event(organizer_id: int, genre_id: int):
        # Создаем событие
        event = Event(
            name=fake.sentence(),
            description=fake.text(),
            expectedAmount=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            recommendedDonation=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            validateStatus=ValidateStatusEnum.REQUIRED,
            countOfMembers=fake.random_int(),
            status=StatusEnum.ACTIVE,
            concession=fake.text(),
            genreId=genre_id,
            organizerId=organizer_id
        )

        # Сохраняем событие в базу данных
        db.session.add(event)
        db.session.commit()
        return event

    def create_ticket(event_dates_id: int, booking_id: int):
        # Создаем билет
        ticket = Ticket(
            dateTime=datetime.now(),
            ticketType=TicketTypeEnum.NUMERIC,
            seat=1,
            eventDatesId=event_dates_id,
            bookingId=booking_id
        )

        # Сохраняем билет в базу данных
        db.session.add(ticket)
        db.session.commit()
        return ticket

    def create_venue(country_id: int, state_id: int, city_id: int, event_id: int):
        # Создаем место проведения
        venue = Venue(
            name=fake.company(),
            description=fake.text(),
            photos=[fake.image_url() for _ in range(2)],
            address=fake.address(),
            seats=fake.random_int(),
            countryId=country_id,
            stateId=state_id,
            cityId=city_id,
            eventId=event_id
        )

        # Сохраняем место проведения в базу данных
        db.session.add(venue)
        db.session.commit()
        return venue

    def create_country():
        # Создаем страну
        country = Country(
            name=fake.country()
        )

        # Сохраняем страну в базу данных
        db.session.add(country)
        db.session.commit()
        return country

    def create_state(country_id: int):
        # Создаем штат
        state = State(
            name=fake.region(),
            countryId=country_id
        )

        # Сохраняем штат в базу данных
        db.session.add(state)
        db.session.commit()
        return state

    def create_city(state_id: int):
        # Создаем город
        city = City(
            name=fake.city(),
            stateId=state_id
        )

        # Сохраняем город в базу данных
        db.session.add(city)
        db.session.commit()
        return city

    def create_event_dates(event_id: int):
        # Создаем даты события
        event_dates = EventDates(
            startDateTime=datetime.now(),
            endDateTime=datetime.now(),
            eventId=event_id
        )

        # Сохраняем даты события в базу данных
        db.session.add(event_dates)
        db.session.commit()
        return event_dates

    def create_event_donation():
        # Создаем пожертвование на событие
        event_donation = EventDonation(
            dateTime=datetime.now(),
            amount=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            comment=fake.text(),
            userId=1,
            eventId=1
        )

        # Сохраняем пожертвование на событие в базу данных
        db.session.add(event_donation)
        db.session.commit()

    def create_booking(event_id: int, user_id: int):
        # Создаем бронирование
        booking = Booking(
            eventId=event_id,
            userId=user_id
        )

        # Сохраняем бронирование в базу данных
        db.session.add(booking)
        db.session.commit()
        return booking

    def create_category():
        # Создаем категорию
        category = Category(
            name=fake.word()
        )

        # Сохраняем категорию в базу данных
        db.session.add(category)
        db.session.commit()
        return category

    def create_genre(category_id: int):
        # Создаем жанр
        genre = Genre(
            name=fake.word(),
            categoryId=1
        )

        # Сохраняем жанр в базу данных
        db.session.add(genre)
        db.session.commit()
        return genre

    def create_feedback():
        # Создаем отзыв
        feedback = Feedback(
            description=fake.text(),
            rate=fake.random_int(min=1, max=5),
            dateTime=datetime.now(),
            photos=[fake.image_url() for _ in range(2)],
            eventId=1,
            userId=1
        )

        # Сохраняем отзыв в базу данных
        db.session.add(feedback)
        db.session.commit()
        return feedback

    def create_favourite_organizer(user_id: int, organizer_id: int):
        # Создаем избранного организатора
        favourite_organizer = FavouriteOrganizer(
            dateTime=datetime.now(),
            userId=user_id,
            organizerId=organizer_id
        )

        # Сохраняем избранного организатора в базу данных
        db.session.add(favourite_organizer)
        db.session.commit()
        return organizer

    create_role()
    create_user("test@gmail.com", "test@gmail.com")

    category = create_category()
    genre = create_genre(category.id)

    for i in range(1, 4):
        user = create_user(f"test{i}@gmail.com", f"test{i}@gmail.com")
        organizer = create_organizer(user.id)
        country = create_country()
        state = create_state(country.id)
        city = create_city(state.id)
        for _ in range(4):
            event = create_event(organizer.id, genre.id)
            create_event_dates(event.id)
            create_venue(country.id, state.id, city.id, event.id)

    # create_booking(event.id, user.id)
    # create_favourite_organizer(user.id, organizer.id)
    # create_feedback()
    # create_event_donation()
    # create_ticket()


if __name__ == '__main__':
    mock_database()
