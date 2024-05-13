import asyncio, quart, hypercorn, json
from quart import render_template
from datetime import datetime

app = quart.Quart(__name__)


@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/commissions')
async def commissions():
    return await render_template('commissions.html')

@app.route('/gallery')
async def gallery():
    gallery_html = ""
    with open('art.json') as f:
        artfile = json.load(f)
        for art in reversed(artfile):
            try:
                art_date = datetime.strftime(datetime.strptime(art["date"], "%y-%m-%d"), "%B %d, %Y")
                art_type = f'{["", "solo ", "duo ", "trio ", "quartet ", "quintet "][art["subjects"]]}{art["type"]}'
                art_html = f'<img src="static/img/art/{art["filename"]}" alt="{art_type} from {art_date}" width="auto" height="auto"/>'
                if art["link"]:
                    art_html = f'<a target="_blank" href="{art["link"]}">{art_html}</a>'
                gallery_html += f'    <div>{art_html}<div><b>{art_date}</b><br><span style="font-size:0.9em">{art_type}</span></div></div>\n'
            except Exception as e:
                print(e)
                continue
    return await render_template('gallery.html', gallery_html=gallery_html)


@app.route('/comms')
async def sona_redirect():
	return quart.redirect(quart.url_for('commissions'), code=301)

@app.route('/favicon.ico')
@app.route('/sitemap.xml')
@app.route('/robots.txt')
async def static_from_root():
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])


hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:11032"]
app.jinja_env.cache = {}

if __name__ == '__main__':
    asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
