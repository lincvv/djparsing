from time import sleep, strftime
from djparsing.core import Parser
from djparsing.data import BodyCssSelect, TextContentCssSelect, AttrCssSelect, TextCssSelect, ImgCssSelect, \
    ExtraDataField

print(strftime('[%H: %M: %S]'), end=' ')
print('********************START*********************')

LIST_WORDS = ['Python', 'Django', 'Питон', 'Flask', 'PyDev', 'sanic', 'aiohttp', '2018', 'vue', 'computer', '404',
              'tproger', 'arm']


class HabrBlog(Parser):
    b = BodyCssSelect(body_count=5)
    text = TextContentCssSelect()
    source = AttrCssSelect(attr_data='href')
    title = TextCssSelect()
    img = ImgCssSelect('src')


data_habr= {
    'b': 'div.posts_list > ul.content-list > li.content-list__item > article.post_preview',
    'text': 'div.post__body_crop > div.post__text',
    'source': 'h2.post__title > a',
    'title': 'h2.post__title > a',
    'img': '.post__body_crop > .post__text img',
}


obj_habr_blog = HabrBlog(
    url='https://habrahabr.ru/hub/django/',
    **data_habr
)


# class HabrAll(HabrBlog):
#
#     class Meta:
#         coincidence = LIST_WORDS
#         field_coincidence = 'title'
#
#
# obj_habr_all = HabrAll(
#     url='https://habrahabr.ru',
#     **data_habr
# )


class RealPython(HabrBlog):
    b = BodyCssSelect(body_count=5,
                      start_url='html body div.container.main-content div.row div.col-12.col-md-6.col-lg-4.mb-5 div.card.border-0 > a',
                      add_domain=True)
    source = AttrCssSelect(attr_data='href', add_domain=True, save_start_url=True)


obj_realpython = RealPython(
    b='div.main-content',
    text='div.article-body > p',
    source='div.col-12 > a',
    title='h1',
    img='figure.embed-responsive > img.card-img-top',
    url='https://realpython.com/blog/'

)


# class PythonzPars(Parser):
#     start = BodyCssSelect(start_url='div.listing_item > div.description > a', add_domain=True, body_count=45)
#     source = AttrCssSelect(attr_data="src")
#     title = AttrCssSelect("data-geopattern")
#     url = ExtraDataField(save_start_url=True)


# obj_pthonz = PythonzPars(
#     start='div.col-md-9',
#     source="div.col-md-9 > div > iframe",
#     title="div > h1",
#     url='http://pythonz.net/videos/'
# )


class ItProgerPars(Parser):
    source = ExtraDataField(save_start_url=False)
    body = BodyCssSelect(body_count=7)
    img = ImgCssSelect('data-lazy-src')
    text = TextContentCssSelect()
    title = TextCssSelect()

    class Meta:
        coincidence = LIST_WORDS
        field_coincidence = 'title'


data_itproger = {
    'body': 'article.post',
    'text': 'div.post-text > div.entry-content > p',
    # 'source': '.post-title .title-box .entry-title a',
    # 'title': 'div.post-text > div.post-title > h2.entry-title',
    # 'img': 'div.entry-image > img',
    'url': 'https://tproger.ru'
}
obj_itproger = ItProgerPars(**data_itproger)

# obj_itproger = ItProgerPars(
#     body="div#content > article.box",
#     text="div.entry-container > div.entry-content > p",
#     source=".post-title .title-box .entry-title a",
#     title=".post-title > h1.entry-title",
#     img="div.entry-image > img",
#     url='https://tproger.ru'
# )


if __name__ == '__main__':
    # obj_itproger.run(log=True)
    # obj_pthonz.run(log=True)
    # res = obj_habr_all.run()
    obj_habr_blog.run(log=True, create=False)
    obj_realpython.run(log=True, create=False)
    print(strftime('[%H: %M: %S]'), end=' ')
    print('********************END*********************')


