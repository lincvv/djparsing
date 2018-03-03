from djparsing.core import Parser
from djparsing.data import BodyCssSelect, TextContentCssSelect, AttrCssSelect, TextCssSelect, ImgCssSelect, \
    ExtraDataField


class ParsCustom(Parser):
    def create(self, data):
        print(data['source'])


class HabrBlog(ParsCustom):
    b = BodyCssSelect(body_count=13)
    text = TextContentCssSelect()
    source = AttrCssSelect(attr_data='href')
    title = TextCssSelect()
    img = ImgCssSelect('src')


data_habr_blog = {
    'b': 'div.posts_list > ul.content-list > li.content-list__item > article.post_preview',
    'text': 'div.post__body_crop > div.post__text',
    'source': 'h2.post__title > a',
    'title': 'h2.post__title > a',
    'img': '.post__body_crop > .post__text img',
}


obj_habr_blog1 = HabrBlog(
    url='https://habrahabr.ru/hub/django/',
    **data_habr_blog
)

LIST_WORDS = ['Python', 'Django', 'Питон', 'Flask', 'PyDev', 'sanic', 'aiohttp', '2018', 'vue']


class HabrAll(HabrBlog):

    class Meta:
        coincidence = LIST_WORDS
        field_coincidence = 'title'


obj_habr_all = HabrAll(
    url='https://habrahabr.ru',
    **data_habr_blog
)


class RealPython(HabrBlog):
    source = AttrCssSelect(attr_data='href', add_domain=True)


obj_realpython = RealPython(
    b="div.col-12.mb-3",
    text="div.card > div.card-body > p.my-1",
    source="div.card > a",
    title="div.card > div.card-body > a > h2.card-title",
    img="div.card > a > img.card-img-top",
    url='https://realpython.com/blog/'

)


class PythonzPars(ParsCustom):
    start = BodyCssSelect(start_url='div.listing_item > div.description > a', add_domain=True, body_count=15)
    source = AttrCssSelect(attr_data="src")
    title = AttrCssSelect("data-geopattern")


obj_pthonz = PythonzPars(
    start='div.col-md-9',
    source="div.col-md-9 > div > iframe",
    title="div > h1",
    url='http://pythonz.net/videos/'
)


class QuestPars(ParsCustom):
    start = BodyCssSelect(start_url='ul.quest-tiles > li.quest-tile-1 > div.item-box > div.item-box-desc h4  a',
                          add_domain=True,
                          body_count=4)
    source = ExtraDataField(save_start_url=True)
    title = TextContentCssSelect(save_start_url=True)
    time = AttrCssSelect('href')


obj_quest = QuestPars(
    start='body > div#wrapper',
    # source="div.col-md-9 > div > iframe",
    title="section.masthead div.container > h1",
    time="section.main-info div div.description-photo > div.price a.btn",
    url='http://mir-kvestov.ru/'
)


class Timepars(ParsCustom):
    data_ = TextContentCssSelect()
    body = BodyCssSelect()


# for data in obj:
#     obj_time = Timepars(
#         body="div#wrapper section.timetable-section > div.timetable > div.timetable_row",
#         data="div.slots",
#         url=data['source']
#     )


if __name__ == '__main__':
    obj_quest.run(log=True)