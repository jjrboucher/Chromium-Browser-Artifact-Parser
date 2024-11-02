# from https://gist.github.com/simon816/afde4d57d5dab8e80120e35596008834
# See https://chromium.googlesource.com/chromium/src/+/master/components/bookmarks/browser/bookmark_codec.cc
def regen_checksum(roots):
    from hashlib import md5
    digest = md5()
    def digest_url(url):
        digest.update(url['id'].encode('ascii'))
        digest.update(url['name'].encode('UTF-16-LE'))
        digest.update(b'url')
        digest.update(url['url'].encode('ascii'))
    def digest_folder(folder):
        digest.update(folder['id'].encode('ascii'))
        digest.update(folder['name'].encode('UTF-16-LE'))
        digest.update(b'folder')
        for child in folder['children']:
            update_digest(child)
    def update_digest(node):
        {
            'folder': digest_folder,
            'url': digest_url
        }[node['type']](node)
    update_digest(roots['bookmark_bar'])
    update_digest(roots['other'])
    update_digest(roots['synced'])
    return digest.hexdigest()

if __name__ == '__main__':
    import json
    from hashlib import md5
    bmpath = 'C:/Users/MDF/AppData/Local/Google/Chrome/User Data/Profile 3/Bookmarks'
    with open(bmpath, 'r', encoding='utf8') as f:
        bookmarks = json.load(f)
    print(regen_checksum(bookmarks['roots']))