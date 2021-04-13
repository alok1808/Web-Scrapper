from flask import Flask, render_template, request
import pymongo
from bs4 import BeautifulSoup
import requests
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        search = request.form.get('search').replace(' ', '')
        try:
            db_conn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = db_conn['crawlerDB']
            reviews = db[search].find({})
            if reviews.count() > 0:
                return render_template('result.html', reviews=reviews)
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + search
                req = requests.get(flipkart_url)
                soup = BeautifulSoup(req.text, "html.parser")
                link = soup.findAll("div", {"class": "_3O0U0u"})
                product_link = "https://www.flipkart.com" + link[0].div.div.a['href']
                link_req = requests.get(product_link)
                r = BeautifulSoup(link_req.text, 'html.parser')
                review_link = r.findAll("div", {"class": "col _39LH-M"})
                r_link = "https://www.flipkart.com" + review_link[0].findAll('a')[-1]['href']
                link = requests.get(r_link)
                review_page = BeautifulSoup(link.text, 'html.parser')
                review_list = review_page.findAll("div", {"class": "_1PBCrt"})

                table = db[search]

                reviews = []
                for review in review_list:
                    try:
                        name = review.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        rating = review.div.div.div.div.text

                    except:
                        rating = 'No Rating'

                    try:
                        comment_head = review.div.div.div.p.text

                    except:
                        comment_head = 'No Comment Heading'

                    try:
                        comtag = review.div.div.find_all('div', {'class': ''})
                        comment = comtag[0].div.text

                    except:
                        comment = 'No Comment '

                    dictionary = {'Name': name, 'Rating': rating, 'CommentHead': comment_head,
                                  'Comment': comment}
                    table.insert_one(dictionary)
                    reviews.append(dictionary)
                return render_template('result.html', reviews=reviews)

        except:
            return "Something went wrong"

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
