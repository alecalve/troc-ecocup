from database import db
import datetime


class User(db.Model):
    login = db.Column(db.String(8), primary_key=True)
    email = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean(), default=False)
    date_join = db.Column(db.DateTime())
    last_login = db.Column(db.DateTime())

    collections = db.relationship('Collection', backref='user', lazy='dynamic')

    def __init__(self, login):
        self.login = login
        self.email = "%s@etu.utc.fr" % login
        self.date_join = datetime.datetime.utcnow()
        self.last_login = datetime.datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.login


class ExchangeMetadata(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    giver_id = db.Column(db.String(8), db.ForeignKey('user.login'))
    receiver_id = db.Column(db.String(8), db.ForeignKey('user.login'))
    date_execution = db.Column(db.DateTime(), default=None)
    date_conf_giver = db.Column(db.DateTime(), default=None)
    date_conf_receiver = db.Column(db.DateTime(), default=None)
    date_cancelled = db.Column(db.DateTime(), default=None)
    canceller = db.Column(db.String(8), default=None)
    date_creation = db.Column(db.DateTime())

    data = db.relationship("ExchangeData", backref="exchange")
    giver = db.relationship("User", foreign_keys="ExchangeMetadata.giver_id")
    receiver = db.relationship("User", foreign_keys="ExchangeMetadata.receiver_id")

    def __init__(self, giver, receiver):
        self.giver_id = giver
        self.receiver_id = receiver
        self.date_creation = datetime.datetime.utcnow()

    def __repr__(self):
        return '<EchangeMetadata %r>' % self.id


class ExchangeData(db.Model): 
    id = db.Column(db.Integer(), primary_key=True)
    exchange_id = db.Column(db.Integer(), db.ForeignKey('exchange_metadata.id'))
    good_id = db.Column(db.Integer(), db.ForeignKey('good.id'))
    giver = db.Column(db.String(8), db.ForeignKey('user.login'))

    good = db.relationship("Good")

    def __init__(self, exchange, good, giver):
        self.exchange_id = exchange
        self.good_id = good
        self.giver = giver

    def __repr__(self):
        return '<EchangeData %r>' % self.id


class Good(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(50))
    semestre = db.Column(db.String(3))
    asso = db.Column(db.String(50))
    nb_exemplaires = db.Column(db.Integer())
    contenance = db.Column(db.Integer())
    appreciation = db.Column(db.Integer(), default=0)
    commentaires = db.Column(db.String(140))

    collections = db.relationship('Collection', backref='good_ref', lazy='dynamic')

    def __repr__(self):
        return '<Good %r>' % self.id


class Collection(db.Model):
    """
    Collection represents what the users have.
    In order for announces to be valid, the announcer MUST have the goods
    he wishes to exchange, if a user loses a good, any announce tied to it
    becomes invalid
    """

    id = db.Column(db.Integer(), primary_key=True)
    login_user = db.Column(db.String(8), db.ForeignKey('user.login'), index=True)
    good_id = db.Column(db.Integer(), db.ForeignKey('good.id'), index=True)
    # value represents how many distinct other goods the user wants in exchange of this one
    # or how many distinct good he is ready to give away to get it 
    value = db.Column(db.Integer(), default=1)
    has_it = db.Column(db.Boolean(), default=False)
    wishes_it = db.Column(db.Boolean(), default=False)
    # A good is locked when an exchange is pending
    locked = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime())
    last_updated = db.Column(db.DateTime())
    date_given = db.Column(db.DateTime(), default=None)

    good = db.relationship("Good")

    def __init__(self, login_user, good):
        self.login_user = login_user
        self.good_id = good
        self.created_at = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Collection %r>' % self.id


class Like(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(8), db.ForeignKey('user.login'))
    good = db.Column(db.Integer())
    valeur = db.Column(db.Integer())

    def __repr__(self):
        return '<Like %r>' % self.id
