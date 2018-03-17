from time import sleep, strftime
from djparsing.core import Parser
from djparsing.data import BodyCssSelect, TextContentCssSelect, AttrCssSelect, TextCssSelect, ImgCssSelect, \
    ExtraDataField

print(strftime('[%H: %M: %S]'), end=' ')
print('********************START*********************')


class HabrBlog(Parser):
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


LIST_WORDS = ['Python', 'Django', 'Питон', 'Flask', 'PyDev', 'sanic', 'aiohttp', '2018', 'vue', 'computer']


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


class PythonzPars(Parser):
    start = BodyCssSelect(start_url='div.listing_item > div.description > a', add_domain=True, body_count=45)
    source = AttrCssSelect(attr_data="src")
    title = AttrCssSelect("data-geopattern")
    url = ExtraDataField(save_start_url=True)


obj_pthonz = PythonzPars(
    start='div.col-md-9',
    source="div.col-md-9 > div > iframe",
    title="div > h1",
    url='http://pythonz.net/videos/'
)


class ItProgerPars(Parser):
    source = ExtraDataField(save_start_url=True)
    body = BodyCssSelect(
        start_url='article > div.entry-image a',
        body_count=3)
    img = ImgCssSelect('data-lazy-src')
    text = TextContentCssSelect()
    title = TextCssSelect()

    class Meta:
        coincidence = LIST_WORDS
        field_coincidence = 'title'


obj_itproger = ItProgerPars(
    body="div.container div#content > article.post",
    text="div.entry-container > div.entry-content > p",
    source=".post-title .title-box .entry-title a",
    title=".post-title > h1.entry-title",
    img="div.entry-image > a > img",
    url='https://tproger.ru'
)


if __name__ == '__main__':
    obj_itproger.run(log=True)
    obj_pthonz.run(log=True)
    print(strftime('[%H: %M: %S]'), end=' ')
    print('********************END*********************')


