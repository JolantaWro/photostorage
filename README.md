# Photo storage project
> An application allowing for the collection of photos in one place. The user has an individual account where links 
> to previously uploaded photos are stored. The main functionalities include logging in, viewing a list of uploaded 
> photos, and adding a new photo.
> Live preview is currently under construction [_web-production-1d39.up.railway.app_](https://web-production-1d39.up.railway.app/).



## General Information
Project written in Django REST Framework, that allows the User to upload an image in PNG or JPG format. User are created 
via the admin panel and added to specific Group: Basic, Premium and Enterprise.

Users that have "Basic" plan after uploading an image get a link to a thumbnail that's 200px in height.

Users that have "Premium" plan get a link to a thumbnail that's in height 200px, 400px, a link to the originally 
uploaded image.

Users that have "Enterprise" plan get a link to a thumbnail that's in height 200px, 400px, a link to the originally 
uploaded image and ability to fetch an expiring link to the image (the link expires after a given number of seconds x
(the user can specify any number between 300 and 30000))

Admin can create arbitrary thumbnail sizes, view the link of the originally uploaded file and ability to
generate expiring links.


## Setup
Download repository `git clone https://github.com/JolantaWro/photostorage.git`

In order to run the application environment is required:
- Installing [_Docker_](https://docs.docker.com/engine/install) according to the Docker project documentation.
- Installing [_Docker Compose_](https://docs.docker.com/compose/install/) for Linux (Docker for Windows and 
- Mac comes with this software built-in).

The project requires adding an .env file with SECRET_KEY. Add the .env file to the root directory of the project.


In order to launch the project, it is necessary to perform: `docker-compose up` (remember to log in to Docker).
Make sure the Docker containers are running and the application is accessible. 

Then perform the migration `docker-compose exec web python manage.py makemigrations` and 
`docker-compose exec web python manage.py migrate`

The project requires an administrator account, which creates users and assigns them to Groups. To do this, 
run the command `docker-compose exec web python manage.py createsuperuser`

After successfully launching the project, open http://localhost:8000/admin and log in with a superuser account
(he will be the site administrator).

The Administrator creates three Groups of accounts: Basic, Premium and Enterprise. Then he adds permissions to the groups:
- photo | photo Can add photo, 
- photo | photo Can change photo, 
- photo | photo Can delete photo, 
- photo | photo Can view photo. 

Now Administrator can create users. Administrator also can change the height of thumbnail images, view the link to the originally uploaded file and
add time to make ability to generate expiring links.
Create several users and use applications http://localhost:8000.





