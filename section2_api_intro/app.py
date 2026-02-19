from flask import Flask, request

app = Flask(__name__)

lst = ['Abbasa', 'Moataza', 'Lotfia', 'Mahmouda', 'Sawsan', 'Fawzia']

@app.route('/show', methods=['GET'])
def show_data():
    return lst

@app.route('/add', methods=['POST'])
def add_data():
    data = request.form.get('item')
    lst.append(data)
    return 'Added Successfully'

@app.route('/update', methods=['PUT'])
def update_data():
    data = request.form
    old = data.get('old')
    new = data.get('new')
    i = lst.index(old)
    lst[i] = new
    return 'Updated Successfully'

@app.route('/delete', methods=['DELETE'])
def delete_data():
    item = request.form.get('item')
    lst.remove(item)
    return 'Deleted Successfully'

app.run(port=5040)
