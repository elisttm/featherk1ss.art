import asyncio, quart, hypercorn, json, os
from quart import render_template
from datetime import datetime

app = quart.Quart(__name__)
path = os.path.dirname(os.path.realpath(__file__))+'/' # this is stupid

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/commissions')
async def commissions():
    return await render_template('commissions.html')

@app.route('/gallery')
async def gallery():
    gallery_html = ""
    with open(path+"art.json") as f:
        for art in reversed(json.load(f)):
            try:
                # {"date": "", "type": "", "subjects": 0, "filename": "", "link": ""},
                art_date = datetime.strftime(datetime.strptime(art["date"], "%y-%m-%d"), "%B %d, %Y")
                art_type = f'{["", "solo ", "duo ", "trio ", "quartet ", "quintet "][art["subjects"]]}{art["type"]}'
                art_html = f'<img src="static/img/art/{art["filename"]}" alt="{art_type} from {art_date}" width="auto" height="auto" loading="lazy"/>'
                if art["link"]:
                    art_html = f'<a target="_blank" href="{art["link"]}">{art_html}</a>'
                gallery_html += f'    <div>{art_html}<div><b>{art_date}</b><br><span style="font-size:0.9em">{art_type}</span></div></div>\n'
            except Exception as e:
                print(e)
                continue
    return await render_template('gallery.html', gallery_html=gallery_html)


@app.route('/comms')
async def comms_redirect():
	return quart.redirect(quart.url_for('commissions'), code=301)

@app.route('/favicon.ico')
@app.route('/sitemap.xml')
@app.route('/robots.txt')
async def static_from_root():
	return await quart.send_from_directory(app.static_folder, quart.request.path[1:])

@app.errorhandler(404)
@app.errorhandler(500)
async def error_handling(error):
	response = quart.Response(await render_template('error.html', errors={
		404: ["[404] page not found", "the url youre trying to access does not exist! you likely followed a dead link or typed something wrong"],
		500: ["[500] internal server error", "somewhere along the way there was an error processing your request. if this keeps happening, please get in contact",],
	}, error=error,), error.code)
	response.headers.set("X-Robots-Tag", "noindex")
	return response

hyperconfig = hypercorn.config.Config()
hyperconfig.bind = ["0.0.0.0:11032"]
app.jinja_env.cache = {}

if __name__ == '__main__':
    asyncio.run(hypercorn.asyncio.serve(app, hyperconfig))
