# 프로젝트: 카탈로그(Item Catalog) 앱

카탈로그(Item Catalog) 앱은 파이썬 플라스크 프레임워크를 활용한 웹 애플리케이션으로서, 여러 장르의 게임들의 리스트를 보여주며, 게임을 생성/수정/삭제할 수 있습니다. 또한 [구글 플러스](https://developers.google.com/identity/protocols/OAuth2)와 [페이스북](https://developers.facebook.com/docs/facebook-login/web)의 OAuth 2.0 사용자 인증 및 등록 시스템을 활용하여 로그인/아웃 기능을 구현하였습니다. 이 앱은 [Udacity의 풀스택 웹개발자 과정](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)의 일환으로 제작되었습니다.

- 영문 리드미(Engilsh README) 파일: [README.md](/README.md)

## 데모
데모 웹사이트 URL: https://itemcatalog.youngsappworkshop.com

## 어플리케이션 설치
깃허브 저장소를 복제(clone)하고, 필요한 패키지를 설치합니다. 파이썬 3.x 버전의 패키지 관리자(python3-pip)가 필요합니다.

```
git clone https://github.com/YoungsAppWorkshop/itemcatalog
cd itemcatalog
sudo pip3 install -r requirements.txt
```

## 어플리케이션 시작
카탈로그(Item Catalog) 앱의 사용자 인증은 [구글 플러스](https://developers.google.com/identity/protocols/OAuth2)와 [페이스북](https://developers.facebook.com/docs/facebook-login/web)의 OAuth 2.0 API를 기반으로 제작되었습니다. 각각의 개발자 페이지에서 API를 생성하고 아래의 설명과 같이 클라이언트 시크릿을 JSON 파일에 저장합니다.

1. 구글 OAuth API를 등록하고 클라이언트 시크릿 파일을 다운받아서 `google_client_secrets.json` 파일에 저장합니다.
2. 페이스북 App ID와 App Secret을 `fb_client_secrets.json` 파일에 기입합니다.

클라이언트 시크릿을 JSON 파일에 저장한 후, 아래와 같이 어플리케이션을 실행시킬 수 있습니다.

```
python3 run.py
```

## 어플리케이션 구조
```bash
└── itemcatalog
    ├── app
    │   ├── mod_api                 # API 관련 모듈
    │   ├── mod_auth                # 사용자 인증 관련 모듈
    │   ├── mod_catalog             # 카탈로그 관련 모듈
    │   ├── static                  # 정적 파일 (.css, .js 등)
    │   ├── templates               # 템플릿 파일
    │   ├── __init__.py             # 애플리케이션 파일
    │   └── models.py               # 데이터베이스 스키마 정의
    ├── uploads                     # 업로드된 이미지 파일
    │   ...
    ├── catalog.db                  # 샘플 데이터베이스
    ├── config.py                   # 설정 파일
    ├── fb_client_secrets.json      # 페이스북 클라이언트 시크릿
    ├── google_client_secrets.json  # 구글 클라이언트 시크릿
    ├── README_ko.md
    ├── README.md
    └── run.py                      # 어플리케이션 실행파일
```

## JSON API로의 접근
카탈로그(Item Catalog) 앱은 등록된 게임과 관련된 정보에 쉽게 접근할 수 있도록, JSON API를 제공합니다. `http://YOUR_SERVER_NAME(서버명)/api`로 API에 접근할 수 있습니다.

1. `/api/categories/all/` : 모든 등록된 게임 정보를 반환
2. `/api/categories/<int:category_id>/items/all/` : 특정한 장르의 등록된 모든 게임 정보를 반환
3. `/api/categories/<int:category_id>/items/<int:item_id>/` : 특정 장르의 특정 게임 정보를 반환
3. `/api/users/all/` : 모든 등록된 사용자에 관한 정보를 반환

## 참고 자료

카탈로그(Item Catalog) 앱은 [Flask](http://flask.pocoo.org/), [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/), [SQLAlchemy](https://www.sqlalchemy.org/), [Jinja2 Templates](http://jinja.pocoo.org/docs/2.10/), [httplib2](https://github.com/httplib2/httplib2), [oauth2client](https://github.com/google/oauth2client), [Bootstrap4](https://v4-alpha.getbootstrap.com/) 등의 라이브러리를 활용하여 제작되었습니다. 아래는 애플리케이션 제작 시 참고한 자료의 목록입니다.

1. [Flask Uploading File pattern](http://flask.pocoo.org/docs/0.12/patterns/fileuploads/) - 이미지 업로드 관련
2. [Google OAuth Sample code from Udacity](https://github.com/udacity/OAuth2.0) - 구글 플러스 OAuth 로그인 구현

## 라이센스
[MIT license](/LICENSE)
