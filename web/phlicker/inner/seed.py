from app import db, User, Album, Photo
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} CHAL_DOMAIN FLAG")
        sys.exit(1)

    if len(User.query.all()) > 0:
        sys.exit(0)

    admin = User(name='admin')
    db.session.add(admin)
    db.session.commit()

    an_album = Album(creator_id=admin.id, title="Take One", description="This is my first photo album!", draft=False)
    db.session.add(an_album)
    db.session.commit()

    for photo in os.listdir("static/photos"):
        photo = Photo(album_id=an_album.id, url=f"http://{sys.argv[1]}/static/photos/{photo}")
        db.session.add(photo)

    db.session.commit()

    flag_album = Album(creator_id=admin.id, title="The Flag", description=sys.argv[2], draft=True)
    db.session.add(flag_album)
    db.session.commit()

    photo = Photo(album_id=flag_album.id, url="TODO: URL TO IMAGE OF FLAG")
    db.session.add(photo)
    db.session.commit()
