from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)
con = psycopg2.connect(host='localhost',database='postgres',user='',password='')
cursor = con.cursor()

@app.route('/api/books/',methods=['POST'])
def create_book():
	try:

		data = request.json
		title = data['title']
		author = data['author']
		genre = data['genre']
		availability = data['availability']
		insert_query = 'Insert into book(title,author,genre,availability) values(%s,%s,%s,%s) RETURNING book_id'
		cursor.execute(insert_query,(title,author,genre,availability))
		
		inserted_id = cursor.fetchone()[0]
		con.commit()

		return jsonify({"message":"Book created successfully","book_id":inserted_id}), 200

	except Exception as e:
		print(e)
		return({"message": "Invalid data"}), 400



@app.route('/api/books/',methods=['GET'])
def get_all_books():
	try:

		select_query = """select * from book;"""
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()
		
		all_books= []
		
		for book in select_cursor:
			x = {"book_id":book[0], 
			"title":book[1], 
			"author":book[2], 
			"genre":book[3], 
			"availability":book[4]
			}
			all_books.append(x)

		con.commit()

		return jsonify({"books":all_books}), 200


	except Exception as e:
		print(e)
		return({'message':'Invalid data'}), 400


@app.route('/api/books/<int:book_id>',methods=['GET'])
def get_book_by_id(book_id):
	try:
		select_query = """ select * from book where book_id = '{}' """.format(book_id)
		cursor.execute(select_query)
		book_cursor = cursor.fetchall()

		book_id=book_cursor[0][0]
		title=book_cursor[0][1]
		author=book_cursor[0][2]
		genre=book_cursor[0][3]
		availability=book_cursor[0][4]


		return jsonify({"book_id":book_id,"title":title,"author":author,"genre":genre,"availability":availability}), 200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/books/<int:book_id>',methods=['PUT'])
def update_book(book_id):
	try:
		data = request.json
		title = data['title']
		author = data['author']
		genre = data['genre']
		availability = data['availability']

		select_query = """ select * from book where book_id = '{}' """.format(book_id)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()
		book_id = select_cursor[0][0]

		update_query = """update book set title = %s, author = %s, genre=%s, availability=%s where book_id= %s"""
		cursor.execute(update_query,(title,author,genre,availability,book_id))

		con.commit()

		return jsonify({"message":"Book updated successfully"})


	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
	try:
		select_query = """ select * from book where book_id = '{}' """.format(book_id)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()

		delete_query = """delete from book where book_id= '{}'""".format(book_id) 
		cursor.execute(delete_query)
		con.commit()

		return jsonify({"message":"Book deleted successfully"}), 200


	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/users',methods=['POST'])
def create_user():
	try:		
		data = request.json 
		name = data['name']
		email = data['email']

		insert_query = """insert into library_user(name,email) values (%s,%s) returning user_id"""
		cursor.execute(insert_query,(name,email))
		user_id = cursor.fetchone()[0]
		con.commit()

		return jsonify({"message":"User created successfully","user_id":user_id}), 200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/users/<int:user_id>/borrow/<int:book_id>',methods=['POST'])
def borrow_book(user_id,book_id):
	try:
		select_query = """ select * from library_user where user_id = '{}' """.format(user_id)
		cursor.execute(select_query)
		user = cursor.fetchone()
		
		if user is not None and len(user)>0:
			book_query = """ select * from book where book_id = '{}' """.format(book_id)
			cursor.execute(book_query)
			book_cursor = cursor.fetchall()
			print(book_cursor)

			if book_cursor is None or len(book_cursor)==0:
				 return jsonify({"message":"Book is not found"}), 404

			availability = book_cursor[0][4]
			if not availability:
				return jsonify({"message":"Book is not available"}), 404


			insert_query = """insert into book_user_mapping(book_id,user_id) values (%s,%s) returning id"""
			cursor.execute(insert_query,(book_id,user_id))

			
			update_query = """update book set availability=%s where book_id= %s"""
			cursor.execute(update_query,(False,book_id))


			con.commit()

			return jsonify({"message": "Book borrowed successfully"}), 200

		else:
			return jsonify({"message":"No user found"}),404


	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}), 400


@app.route('/api/users/<int:user_id>/return/<int:book_id>',methods=['POST'])
def return_book(user_id,book_id):
	try:
		select_query = """ select * from library_user where user_id = '{}' """.format(user_id)
		cursor.execute(select_query)
		user = cursor.fetchone()
		
		if user is not None and len(user)>0:
			book_query = """ select * from book where book_id = '{}' """.format(book_id)
			cursor.execute(book_query)
			book_cursor = cursor.fetchall()
			print(book_cursor)

			if book_cursor is None or len(book_cursor)==0:
				 return jsonify({"message":"Book is not found"}), 404

			availability = book_cursor[0][4]
			if not availability:
				user_query = """select * from book_user_mapping where user_id = '{}' """.format(user_id)
				cursor.execute(user_query)
				user_exist = cursor.fetchone()

				if user_exist is not None and len(user_exist)>0:
					book_exist_query = """ select * from book_user_mapping where book_id = '{}' """.format(book_id)
					cursor.execute(book_exist_query)
					book_exist = cursor.fetchall()

					if book_exist is None or len(book_exist)==0:
				 		return jsonify({"message":"Book is not found"}),404

					delete_query = """delete from book_user_mapping where book_id ='{}' and user_id ='{}'""".format(book_id,user_id)
					cursor.execute(delete_query)
					update_query = """update book set availability=%s where book_id= %s"""
					cursor.execute(update_query,(True,book_id))

					con.commit()

					return jsonify({"message": "Book returned successfully"}), 200

		else:
			return jsonify({"message":"No user found"}),404

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}),400


@app.route('/api/users/<int:user_id>',methods=['DELETE'])
def delete_user(user_id):
	try:
		select_query = """select * from library_user where user_id ='{}'""".format(user_id)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()


		delete_query = """delete from library_user where user_id ='{}' """.format(user_id)
		cursor.execute(delete_query)
		con.commit()

		return jsonify({"message": "User deleted successfully"})

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}),400


@app.route('/api/users/<int:user_id>',methods=['PUT'])
def update_user(user_id):
	try:
		data = request.json 
		name = data['name']
		email = data['email']

		select_query = """select * from library_user where user_id ='{}'""".format(user_id)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()


		update_query = """update library_user set name = '{}' where user_id = '{}'""".format(name,user_id)
		cursor.execute(update_query)
		con.commit()

		return jsonify({"message": "User updated successfully"}), 200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}),400


@app.route('/api/users/<int:user_id>', methods=['GET'])
def getUserById(user_id):
	try:
		select_query = """select * from library_user where user_id = '{}' """.format(user_id)
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()

		user_id = select_cursor[0][0]
		name = select_cursor[0][1]
		email = select_cursor[0][2]

		book_query = """select * from book_user_mapping where user_id ='{}'""".format(user_id)
		cursor.execute(book_query)
		book_cursor = cursor.fetchall()

		borrowed_books = []
		for book in book_cursor:
			book_id = book[1]
			borrowed_books.append(book_id)

		con.commit()
		return jsonify({"user_id": user_id, "name":name, "email":email, "borrowed_books":borrowed_books}), 200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}),400


@app.route('/api/users', methods=['GET'])
def get_users():
	try:
		select_query = """select * from library_user"""
		cursor.execute(select_query)
		select_cursor = cursor.fetchall()

		response = []
		for user in select_cursor:
			user_id = user[0]
			name = user[1]
			email = user[2]

			book_query = """select * from book_user_mapping where user_id = '{}'""".format(user_id)
			cursor.execute(book_query)
			book_cursor = cursor.fetchall()
			

			borrowed_books = []
			for data in book_cursor:
				borrowed_books.append(data[1])


			x = {"user_id": user_id, "name":name, "email":email,"borrowed_books":borrowed_books}
			response.append(x)

		return jsonify({"users":response}), 200

	except Exception as e:
		print(e)
		return jsonify({"message":"Invalid data"}),400



if __name__ == '__main__':
	app.run(port=8080,debug=True)










