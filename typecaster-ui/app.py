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
    podcast = podcasts[int(podcast_id)]
    if request.method == 'GET':
        kwargs = {}
        kwargs['action'] = 'Create'
        kwargs['episode'] = {
            'title': 'Episode ' + str(len(podcast.episodes.keys())),
            'text_format': 'plain'
        }
        kwargs['episode_title'] = 'test'
        return render_template('episode_detail.html', **kwargs)

    if request.method == 'POST':
        synth_args = json.load(open('params.json'))
        podcast.add_episode(request.form['text'], text_format=request.form['text_format'],
                       title=request.form['title'], author=request.form['author'],
                       synth_args=synth_args)
        
        if hasattr(podcast, 'episode_ids'):
            podcast.episode_ids[len(podcast.episodes.keys())] = request.form['title']
        else:
            setattr(podcast, 'episode_ids', {0: request.form['title']})
        
        return redirect(url_for('podcast_detail', podcast_id=podcast_id))

@app.route('/podcasts/<podcast_id>/episodes/<episode_id>')
def episode_detail(podcast_id, episode_id):
    podcast = podcasts[int(podcast_id)]
    episode_title = podcast.episode_ids[int(episode_id)]
    episode = podcast.episodes[episode_title]
    if request.method == 'GET':
        kwargs = {}
        kwargs['podcast_title'] = podcast.title
        kwargs['episode'] = episode
        return render_template('episode_detail.html', **kwargs)
    if request.method == 'POST':
        for key, value in request.form.iteritems():
            if getattr(episode, key) != value:
                 setattr(episode, key, value)
        podcast.update_rss_feed()
        return redirect(url_for('podcast_detail', podcast_id=podcast_id))

if __name__ == '__main__':
    app.run(debug=True)
