# Image hosting app (Flask)

## Description

A demo web application for hosting pictures of user on **Flask**, with following features:

- The app has a very simple front-end part (but not so poor back-end) basen on HTML templates rendered by `Jinja2` (
  without fully adaptive layout)

- Data is stored using **SQLite** DB (created and managed using `flask_sqlalchemy` and `flask_migrate`). ER Diagram of
  the DB model:

![DB_ER_Diagram](readme_img/db_diagram.png)

- The app has full **CRUD** functionality for viewing and managing the pictures
- Validation of the input data during the registration and log in is implemented
  using [`marshmallow`](https://marshmallow.readthedocs.io/en/stable/)
- User's password is stored in encrypted way (**hash** column in the **User** table). Encryption is done
  with [`bcrypt`](https://pypi.org/project/bcrypt/):

```python
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
```

- Uploaded pictures are stores statically in a corresponding to the user folder:

![static](readme_img/static.png)

- "remember me" function is implemented using cookies (`response.set_cookie`)

## Examples of different pages

- Index page:

![index_page](readme_img/index.png)

- Example of the input data validation:

![validation_ex](readme_img/validation.png)

- Pictures of a user:

![user_images](readme_img/user_img.png)

- Upload page:

![upload_page](readme_img/upload.png)

- Page with editing the description of the picture:

![edit_description_page](readme_img/edit_page.png)

**_Kravchenko Michail_**
