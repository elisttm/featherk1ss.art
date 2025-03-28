import asyncio, quart, hypercorn, json, os
from quart import render_template
from datetime import datetime

app = quart.Quart(__name__)
path = os.path.dirname(os.path.realpath(__file__))+'/' # this is stupid

class ff:

    def get_date(art):
        return datetime.strftime(datetime.strptime(art["date"], "%y-%m-%d"), "%B %d, %Y")
    
    def get_type(art):
        return ["", "solo ", "duo ", "trio "][art["subjects"]] + art["type"]


@app.route('/')
async def _index():
    return await render_template('index.html')

@app.route('/commissions')
async def _commissions():
    return await render_template('commissions.html')

@app.route('/gallery')
async def _gallery():
    with open(path+"art.json") as f:
        art_list = json.load(f)
    return await render_template('gallery.html', ff=ff, art_list=art_list)

@app.route('/cupid')
async def _cupid():
	return await render_template('cupid.html')

@app.route('/comms')
@app.route('/tos')
async def redirect_comms():
	return quart.redirect(quart.url_for('_commissions'), code=301)

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
