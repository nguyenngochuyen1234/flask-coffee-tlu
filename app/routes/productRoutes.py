from flask import Blueprint, jsonify, request
from app.models import product
from app.models import typeproduct
from app.schemas import ProductSchema
from app import db
#Bước 3
product_bp = Blueprint('product_bp', __name__)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@product_bp.route('/product', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('Product_Name')
    image = data.get('Product_Image')
    price = data.get('Product_Price')
    description = data.get('Product_Description')
    type_product_id = data.get('TypeProduct_ID')
    if name and image and price and type_product_id:
        check_type_product_id = db.session.query(typeproduct.TypeProduct_ID)\
                                .filter_by(TypeProduct_ID=type_product_id).first() is not None
        check_name = db.session.query(product.Product_Name).filter_by(Product_Name=name).first() is None
        check_image = db.session.query(product.Product_Image).filter_by(Product_Image=image).first() is None

        if check_type_product_id and check_name and check_image:
            try:
                print(data)
                new_product = product(Product_Name=name, Product_Image=image,Product_Price=price
                                        , Product_Description=description
                                        , TypeProduct_ID =type_product_id)
                db.session.add(new_product)
                db.session.commit()
                return jsonify({"data":{"idProduct":new_product.idProduct}}), 200  # Return with HTTP status 201 for created
            except:
                return {
                    'Error': 'ERR',
                },404
        else:
            return {
                    'message': "Trùng tên hoặc link ảnh, hoặc ko tồn tại trong TypeProduct",
                    'status': 400,
                    'Error': 'ERR',
                }, 400
    else:
        return {
                    'message': "Nhập thiếu dữ liệu",
                    'status': 400,
                    'Error': 'ERR',
                }, 400

@product_bp.route('/product', methods=['GET'])
def get_products():
    try:
        products = product.query.join(typeproduct).all()
        product_list = []
        for productItem in products:
            product_list.append({
                'idProduct': productItem.idProduct,
                'Product_Name': productItem.Product_Name,
                'Product_Image': productItem.Product_Image,
                'Product_Price': productItem.Product_Price,
                'Product_Description': productItem.Product_Description,
                'TypeProduct_ID': productItem.TypeProduct_ID,
                'TypeProduct_Name': productItem.type_product.TypeProduct_Name
            })
        return jsonify({"data":product_list})
    except:
        return {
            'Error': 'ERR',
        },404

@product_bp.route('/product/<string:id>', methods=['GET'])
def get_product(id):
    check = db.session.query(product.idProduct).filter_by(idProduct=id).first() is not None
    if check:
        try: 
            product_get_by_id = product.query.get_or_404(id)
            result = product_schema.dump(product_get_by_id)
            return jsonify({"data":result}),200
        except:
            return {
                'Error': 'ERR',
            },404
    else:
        return {
                'message': "KO tìm thấy bản ghi",
                'status': 400,
                'Error': 'ERR',
            }, 400
    
@product_bp.route('/product/<string:id>', methods=['PUT'])
def update_product(id):
    check = db.session.query(product.idProduct).filter_by(idProduct=id).first() is not None
    if check:
        try:
            product_update = product.query.get_or_404(id)
            data = request.get_json()
            name = data.get('Product_Name')
            image = data.get('Product_Image')
            price = data.get('Product_Price')
            description = data.get('Product_Description')
            type_product_id = data.get('TypeProduct_ID')
            if type_product_id: 
                check_type_product_id = db.session.query(typeproduct.TypeProduct_ID).filter_by(TypeProduct_ID=type_product_id).first() is not None
                if check_type_product_id:
                    product_update.Product_Name = name
                    product_update.Product_Image = image
                    product_update.Product_Price = price
                    product_update.Product_Description = description
                    product_update.TypeProduct_ID = type_product_id
                    db.session.commit()
                    return product_schema.jsonify(product_update),200
                else:
                    return {
                        'message': "bản ghi ko tồn tại trong TypeProduct",
                        'status': 400,
                        'Error': 'ERR',
                    }, 400
            else:
                return {
                            'message': "Nhập thiếu dữ liệu",
                            'status': 400,
                            'Error': 'ERR',
                        }, 400
        except:
            return {
                'Error': 'ERR',
            },404
    else:
        return {
                'message': "KO tìm thấy bản ghi",
                'status': 400,
                'Error': 'ERR',
            }, 400

@product_bp.route('/product/<string:id>', methods=['DELETE'])
def delete_product(id):
    check = db.session.query(product.idProduct).filter_by(idProduct=id).first() is not None
    if check:
        print('check:',check)
        try:
            product_delete = product.query.get_or_404(id)
            db.session.delete(product_delete)
            db.session.commit()
            return{
                    'message': 'Da xoa ban ghi',
                    'status': 200,
                }, 200  # Return with HTTP status 204 for no content
        except:
            return {
                'Error': 'ERR',
            },404
    else:
        return {
                'message': "KO tim thay ban ghi",
                'status': 400,
                'Error': 'ERR',
            }, 400
@product_bp.route('/product/search/<string:data_search>', methods=['GET'])
def search_product(data_search):
    try:
        products = product.query.filter(product.Product_Name.like(f"%{data_search}%")).all()
        data = [{'idProduct': product.idProduct, 'Product_Name': product.Product_Name, 'Product_Image': product.Product_Image, 'Product_Price': product.Product_Price } for product in products]
        return jsonify({'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@product_bp.route('/product/getProductByType/<type_id>', methods=['GET'])
def get_products_by_type(type_id):
    products = product.query.join(typeproduct).filter(typeproduct.TypeProduct_ID == type_id).all()
    product_list = []
    for productItem in products:
        product_list.append({
            'idProduct': productItem.idProduct,
            'Product_Name': productItem.Product_Name,
            'Product_Image': productItem.Product_Image,
            'Product_Price': productItem.Product_Price,
            'Product_Description': productItem.Product_Description,
            'TypeProduct_ID': productItem.TypeProduct_ID,
        })
    return jsonify({"data":product_list})
