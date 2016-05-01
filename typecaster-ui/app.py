from flask import Flask, render_template, redirect, url_for, request
from typecaster import Podcast, Episode
import json
# import pickle

app = Flask(__name__)

podcasts = {}

@app.route('/')
def index():
    return redirect(url_for('podcast_list'))

@app.route('/podcasts/')
def podcast_list():
    kwargs = {}
    kwargs['podcasts'] = podcasts
    return render_template('podcast_list.html', **kwargs)

@app.route('/podcasts/new/', methods=['GET', 'POST'])
def create_podcast():
    if request.method == 'GET':
        kwargs = {}
        kwargs['action'] = 'Create'
        kwargs['podcast'] = {
            'title': 'Podcast ' + str(len(podcasts.keys())),
            'link': 'http://test.com'
        }
        kwargs['episodes'] = []
        return render_template('podcast_detail.html', **kwargs)

    if request.method == 'POST':
        new_podcast = Podcast(title=request.form['title'], link=request.form['link'],
                         author=request.form['author'], description=request.form['description'],
                         output_path='.')

        podcasts[len(podcasts.keys())] = new_podcast
        # pickle.dump(dict((key, podcast.title) for key, podcast in podcasts.iteritems()), open( "pod.p", "wb" ))
        return redirect(url_for('podcast_list'))

@app.route('/podcasts/<podcast_id>/', methods=['GET', 'POST'])
def podcast_detail(podcast_id):
    edit_podcast = podcasts[int(podcast_id)]
    if request.method == 'GET':
        kwargs = {}
        kwargs['action'] = 'Edit'
        kwargs['podcast'] = edit_podcast
        kwargs['podcast_id'] = podcast_id
        return render_template('podcast_detail.html', **kwargs)
    if request.method == 'POST':
        for key, value in request.form.iteritems():
            if getattr(edit_podcast, key) != value:
                 setattr(edit_podcast, key, value)
        podcasts[int(podcast_id)] = edit_podcast
        return redirect(url_for('podcast_detail', podcast_id=podcast_id))

@app.route('/podcasts/<podcast_id>/episodes/new/', methods=['GET', 'POST'])
def create_episode(podcast_id):
    if request.method == 'GET':
        kwargs = {}
        kwargs['action'] = 'Create'
        kwargs['episode'] = {
            'title': 'Episode ' + str(len(podcasts[int(podcast_id)].episodes.keys())),
            'text_format': 'plain'
        }
        kwargs['episode_title'] = 'test'
        return render_template('episode_detail.html', **kwargs)

    if request.method == 'POST':
        synth_args = json.load(open('params.json'))
        podcasts[int(podcast_id)].add_episode(request.form['text'], text_format=request.form['text_format'],
                       title=request.form['title'], author=request.form['author'],
                       synth_args=synth_args)
        return redirect(url_for('podcast_detail', podcast_id=podcast_id))

@app.route('/podcasts/<podcast_id>/episodes/<episode_id>')
def episode_detail(podcast_id, episode_id):
    kwargs = {}
    kwargs['podcast_title'] = podcasts[int(podcast_id)].title
    kwargs['episode'] = podcasts[int(podcast_id)].episodes.values()[episode_id]
    return render_template('episode_detail.html', **kwargs)

if __name__ == '__main__':
    app.run(debug=True)