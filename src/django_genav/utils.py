import re


CAMEL_TO_UNDER_PATTERN_1 = re.compile(r'(.)([A-Z][a-z]+)')
CAMEL_TO_UNDER_PATTERN_2 = re.compile(r'([a-z0-9])([A-Z])')


def camel_to_under(name):
    return \
        CAMEL_TO_UNDER_PATTERN_2.sub\
            ( r'\1_\2'
            , CAMEL_TO_UNDER_PATTERN_1.sub(r'\1_\2', name)
            ).lower()

# class ExampleProfileView(View):
#     pass
#
#
# class ExampleProfileNavigation(NavigationModel):
#     name = 'user.detail'
#     view = ExampleProfileView
#     url = \
#         ( '/my/'
#         , '/sim(?P<sim>\d+)/'
#         , '/user/(?P<username>\w+)/'
#         )
#
#
# class ExamplePhotoAlbumView(View):
#     pass
#
#
# class ExamplePhotoAlbumNavigation(NavigationModel):
#     view = ExamplePhotoAlbumView
#     name = 'user.storage.photo.album.list'
#     parent = ExampleProfileView
#     url = \
#         ( 'storage/photo/album/(?P<album_pk>\d+)/'
#         , )
#
#
# class ExamplePhotoView(View):
#     pass
#
#
# class ExamplePhotoNavigation(NavigationModel):
#     view = ExamplePhotoView
#     name = 'user.storage.photo.detail'
#     parent = ExamplePhotoAlbumView
#     url = \
#         ( '(?P<pk>\d+)/'
#         , )
#
#
# class ExamplePhotoDeleteView(View):
#     pass
#
#
# class ExamplePhotoDeleteNavigation(NavigationModel):
#     view = ExamplePhotoDeleteView
#     name = 'user.storage.photo.delete'
#     parent = ExamplePhotoView
#     url_exclude_with_args = \
#         ( 'sim'
#         , 'username'
#         )
#     url = \
#         ( 'delete/'
#         , )
#
#
# """
# expectation
#
# pk
# username / pk
# sim / pk
# """