# python
import requests
from scrapy.selector import Selector
import sqlite3
import re
import pymorphy2
import codecs


class CourseSearch:
    def __init__(self):
        self.conn = sqlite3.connect('courses.db')
        self.c = self.conn.cursor()
        self.c.execute(
            'CREATE TABLE IF NOT EXISTS courses (id integer NOT NULL PRIMARY KEY UNIQUE, cname text, cid integer, pnum integer)')
        self.c.execute('CREATE TABLE IF NOT EXISTS dict (cname text, cid integer)')
        self.morph = pymorphy2.MorphAnalyzer()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def get_page(self, pnum):
        next_page_num = 0
        print(pnum)
        r = requests.get('https://www.hse.ru/edu/courses/page' + str(
            pnum) + '.html?language=&edu_level=&full_words=&genelective=0&xlc=&words=&level=&edu_year=2018&filial=22723&mandatory=&is_dpo=0&lecturer=', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3024.0 Safari/537.36'})
        if r.status_code == 200:
            body = r.text
            # print(body)
            file = codecs.open(pnum +".html", "w", encoding="utf-8")
            file.write(body)
            file.close()

            active_page_num_list = Selector(text=body).css('div.letterlist > span.active ::text').extract()
            if active_page_num_list:
                active_page_num = int(active_page_num_list[0])
                next_page_num = active_page_num + 1
                print(active_page_num, next_page_num)

                all = Selector(text=body).css('div.b-program>div.b-program__inner>div.first_child>h2.doc>a.link')
                for a in all:
                    title = a.css('::text')[0].extract()
                    h = a.css('::attr(href)')[0].extract()
                    course_id_group = re.search('https\:\/\/www\.hse\.ru\/edu\/courses\/(\d+)', h, re.IGNORECASE)
                    if course_id_group:
                        course_id = course_id_group.group(1)
                        print(title, course_id)
                        # (id integer NOT NULL PRIMARY KEY UNIQUE, cname text, cid integer, pnum integer)
                        self.c.execute("INSERT INTO courses(cname, cid, pnum) VALUES ('"+title+"',"+course_id+"," + str(pnum) + ")")
                        last_course_id  = self.c.lastrowid;
                        words  = title.split(' ')
                        # print (words)
                        for w in words:
                            f = self.get_form(w)
                            self.c.execute( "INSERT INTO dict VALUES ('" + f + "'," + str(last_course_id) + ")")
                            print(f)


            else:
                print("error page, stopping...")

            return body
        else:
            print(r.status_code)
        return

    def get_form(self, word):
        return self.morph.parse(word)[0].normal_form

cs  = CourseSearch()


user_response1 = input("Put number to download page or no exit\n")
if user_response1 == "no":
    print("exit")
else:
    if user_response1.isdecimal():
        print("getting data\n")
        cs.get_page(user_response1)
    else:
        print("you put bad command\n")

