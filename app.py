#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # artists = Artist.query.order_by()
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  cities = set()
  for venue in venues:
    cities.add((venue.city, venue.state))
  
  newdata = []

  for city in cities:
    city_venues = Venue.query.filter_by(city=city[0], state=city[1]).all()
    city_data = {
      'city': city[0],
      'state': city[1],
      'venues': city_venues
    }
    newdata.append(city_data)
  
  return render_template('pages/venues.html', areas=newdata)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_query = '%{}%'.format(search_term)
  result = Venue.query.filter(Venue.name.ilike(search_query)).all()
  search_response={
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_venues.html', results=search_response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  current_datetime = datetime.now()
  venue_shows = Show.query.filter_by(venue_id=venue_id)
  past_shows = []
  upcoming_shows = []
  for show in venue_shows:
    show_artist = Artist.query.get(show.artist_id)
    if(show.start_time < current_datetime):
      past_shows.append({
        'artist_id': show_artist.id,
        'artist_name': show_artist.name,
        'artist_image_link': show_artist.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })
    else:
      upcoming_shows.append({
        'artist_id': show_artist.id,
        'artist_name': show_artist.name,
        'artist_image_link': show_artist.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })

  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  data = request.form
  venue = Venue(
    name=data['name'],
    city=data['city'],
    state=data['state'],
    address=data['address'],
    phone=data['phone'],
    image_link=data['image_link'],
    facebook_link=data['facebook_link'],
    genres=data.getlist('genres')
    )
  error = False

  try:
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error: True
  finally:
    db.session.close()

  if(error):
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback
    error = True
  finally:
    db.session.close()

  if(error):
    flash('Venue could not be deleted. try again')
    return

  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_query = '%{}%'.format(search_term)
  result = Artist.query.filter(Artist.name.ilike(search_query)).all()
  search_response={
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_artists.html', results=search_response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = Artist.query.get(artist_id)
  current_datetime = datetime.now()
  artist_shows = Show.query.filter_by(artist_id=artist_id)
  past_shows = []
  upcoming_shows = []
  for show in artist_shows:
    show_venue = Venue.query.get(show.venue_id)
    if(show.start_time < current_datetime):
      past_shows.append({
        'venue_id': show_venue.id,
        'venue_name': show_venue.name,
        'venue_image_link': show_venue.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })
    else:
      upcoming_shows.append({
        'artist_id': show_venue.id,
        'artist_name': show_venue.name,
        'artist_image_link': show_venue.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })

  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  data = request.form
  artist = Artist.query.get(artist_id)
  artist.name = data['name']
  artist.city = data['city']
  artist.state = data['state']
  artist.phone = data['phone'],
  artist.facebook_link = data['facebook_link']
  artist.genres = data.getlist('genres')
  error = False
  try:
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if (error):
    flash('An error occurred. Artist ' + data.name + ' could not be edited.')

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  data = request.form
  venue = Venue.query.get(venue_id)
  venue.name = data['name']
  venue.city = data['city']
  venue.state = data['state']
  venue.address = data['address']
  venue.phone = data['phone'],
  venue.image_link = data['image_link']
  venue.facebook_link = data['facebook_link']
  venue.genres = data.getlist('genres')
  error = False
  try:
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  
  if (error):
    flash('An error occurred. Venue could not be saved.')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data = request.form
  artist = Artist(
    name=data['name'],
    city=data['city'],
    state=data['state'],
    phone=data['phone'],
    image_link=data['image_link'],
    facebook_link=data['facebook_link'],
    genres=data.getlist('genres')
    )
  error = False
  try:
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if (error):
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  shows_data = []
  for show in shows:
    show_artist = Artist.query.get(show.artist_id)
    show_venue = Venue.query.get(show.venue_id)
    shows_data.append({
      "venue_id": show_venue.id,
      "venue_name": show_venue.name,
      "artist_id": show_artist.id,
      "artist_name": show_artist.name,
      "artist_image_link": show_artist.image_link,
      "start_time": show.start_time.strftime("%d-%m-%Y %H:%M:%S")
    })


  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  data = request.form
  show = Show(
    venue_id=data['venue_id'],
    artist_id=data['artist_id'],
    start_time=data['start_time']
  )
  error = False
  try:
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if (error):
    flash('An error occurred. Show could not be listed.')

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
