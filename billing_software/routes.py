from flask import render_template, url_for, redirect, flash, Markup, abort, request, jsonify
from billing_software import app, db, mail, bcrypt, admin
from billing_software.models import Product, Bill, Pdimensions, Pimages, BillProducts
from billing_software.forms import addNewItemForm
from sqlalchemy import asc, desc, update
from flask_mail import Mail, Message
from flask_login import login_user, current_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView

from billing_software.InsertDataIntoBatabase import *
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2
import os
import random
import math
import glob
import sqlite3
# from matplotlib import pyplot as plt

with app.app_context(), app.test_request_context(base_url='E:/TCS Inframind/billing_software/billing_software/'):
    # http://localhost/page/2
    # url = url_for('page', page_number=2, )
    PATH_IMAGES = url_for('static', filename='product_images/', _external=True)


# with app.test_request_context():
#     PATH_IMAGES = url_for("static", filename="product_images/")

files   = glob.glob(PATH_IMAGES+"Pic.png")
files1   = glob.glob(PATH_IMAGES+"Pic1.png")

admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Pdimensions, db.session))
admin.add_view(ModelView(Pimages, db.session))
admin.add_view(ModelView(BillProducts, db.session))
admin.add_view(ModelView(Bill, db.session))


@app.route("/")
@app.route("/login")
def login():
    # print(PATH_IMAGES+'Pic'+'.png')
    return render_template('login.html')

@app.route("/home")
def home():
    print(PATH_IMAGES)
    return render_template('example.html')

# @app.route("/showbills")
# def bills():
#     return render_template('bills.html')

@app.route("/items", methods=['GET', 'POST'])
def items():
    return render_template('items.html')

image_data_array=[]

@app.route("/addImage", methods=['GET', 'POST'])
def addImage():
    #global image_data_array
    Image_Capture()
    (l,w)=Image_Process()
    #image_data_array.append((l, w))
    # for i in image_data_array:
        # print("Now the value of l and w: ")
        # x,y = i[2],i[3]
        # print(x,y)
    return redirect(url_for('addNewItem'))


@app.route("/addNewItem", methods=['GET', 'POST'])
def addNewItem():
    global image_data_array
    for i in image_data_array:
        x,y = i[2],i[3]
        print(x,y)
    form = addNewItemForm()
    if form.validate_on_submit():
        product = Product(
                    name=form.pName.data,
                    price=form.pPrice.data,
                    weight=form.pWeight.data,
                    # my_blob=sqlite3.Binary(image_bytes)
                    )
        db.session.add(product)
        db.session.flush()
        print(len(image_data_array))
        for i in range(len(image_data_array)):
            image = Pimages(
                    pid = product.id,
                    # porig=sqlite3.Binary(image_data_array[i][0]),
                    # pprocess=sqlite3.Binary(image_data_array[i][1])
                )
            db.session.add(image)
            db.session.flush()
            dimensions = Pdimensions(
                pid = product.id,
                length = image_data_array[i][2],
                width = image_data_array[i][3],
                piid = image.id
            )
            db.session.add(dimensions)
            db.session.flush()
        db.session.commit()
        image_data_array = []
        flash('Product has been successfully added.', 'success')
    return render_template('addItems.html', form=form, array = image_data_array)
#
@app.route("/myprofile", methods=['GET', 'POST'])
def myProfile():
    #pass
    return render_template('myprofile.html')
#
@app.route("/generatebills", methods=['GET', 'POST'])
def generatebills():
    return render_template('generatebills.html')

@app.route("/showbills", methods=['GET', 'POST'])
def showbill():
    return render_template('billtable.html')

@app.route("/newbill/<int:bid>", methods=['GET', 'POST'])
def newbill(bid):
    bill_products=0
    quantity = {}
    total=0
    if bid>0:
        all_product_in_cart = []
        bill=Bill.query.get(bid)
        bill_products_id = BillProducts.query.filter_by(bill_id=bid).with_entities(BillProducts.prod_id).all()
        for each_id in bill_products_id:
            each_product = Product.query.get(each_id)
            all_product_in_cart.append(each_product)
            # quantity[each_product.id] = 1
        bill_products = BillProducts.query.filter_by(bill_id=bid)
        for index,bill_quantity in enumerate(bill_products):
            quantity[index] = bill_quantity.pquantity
        print(quantity)
        all_products = BillProducts.query.filter_by(bill_id=bid)
        for each_product in all_products:
            total+=each_product.bill_products.price * each_product.pquantity
            print(total)
        bill.bill_amount=total
        print(bill.bill_amount)
        db.session.commit()
    else:
        bill=None
        all_product_in_cart=None
    return render_template('new_bill.html', bill=bill, bill_products=all_product_in_cart, quantity=quantity)

@app.route("/generateNewBill", methods=['GET', 'POST'])
def generateNewBill():
    bill = Bill()
    # db.session.flush()
    db.session.add(bill)
    db.session.commit()
    return render_template('new_bill.html', bill=bill, bill_products=None, quantity=None)

@app.route("/addProdInCart/<bid>", methods=['GET', 'POST'])
def addProdInCart(bid):
    Image_Capture()
    bill = Bill.query.get(bid)
    bill_products = BillProducts.query.filter_by(bill_id=bid)
    (l,w)=Image_Process()
    product_found = Pdimensions.query.filter_by(length = l, width = w).first()
    if product_found:
        flash('Product Detected', 'success')
        product_added = Product.query.filter_by(id=product_found.pid).first()
        #total_sum_cost = Product.query.filter_by(price_prod=product_found.pid).first()
        all_prod_ids_in_bill = BillProducts.query.filter_by(bill_id=bid).with_entities(BillProducts.prod_id)
        id_list=[]
        for id in all_prod_ids_in_bill:
            id_list.append(id[0])
        print(product_added.id, id_list)
        if product_added.id not in id_list:
            print("we are here")
            bill_product = BillProducts(
                                bill_id = bid,
                                prod_id = product_added.id
                                )
            db.session.add(bill_product)
        # db.session.flush()
        else:
            print("we are here111")
            product_quan_increase = BillProducts.query.filter_by(bill_id=bid, prod_id=product_added.id).first()
            product_quan_increase.pquantity += 1
        db.session.commit()
        return redirect(url_for('newbill', bid=bid))
    flash('Sorry! The Product is not detected. ', 'danger')
    return render_template('new_bill.html', bill=bill, bill_products=bill_products,quantity=0)

@app.route("/FinalGenerateBill/<bid>", methods=['GET', 'POST'])
def FinalGenerateBill(bid):
    db.session.commit()

# def Image_Process():
#     #return (15,20)
#     #return (10,20)
#     return (4,8)


def Image_Capture():
    #Capture the image
    img = cv2.VideoCapture(0)
    return_value, image = img.read()
    cv2.imwrite(PATH_IMAGES+'Pic'+'.png', image)
    #cv2.imshow("Image", image)
    # print(PATH_IMAGES+'Pic'+'.png')

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def Image_Process():
        #load the image, convert it to grayscale, and blur it slightly
        image = cv2.imread(PATH_IMAGES+'Pic'+'.png')
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(img, (5, 5), 0)
        #gray = cv2.blur(img,(7,7))
        gray = cv2.addWeighted(gray,1.5,img,-0.5,0)

        #perform edge detection, then perform a dilation + erosion to close gaps in between object edges
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # find contours in the edge map
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # sort the contours from left-to-right and initialize the 'pixels per metric' calibration variable
        (cnts, _) = contours.sort_contours(cnts)
        #pixelsPerMetric = None

        # loop over the contours individually
        for c in cnts:
                orig = image.copy()
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                # order the points in the contour such that they appear in top-left, top-right, bottom-right, and bottom-left order, then draw the outline of the rotated bounding box
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
                # co-ordinates of the box in clockwise direction
                (t1, tr, br, b1) = box
                (t1trX, t1trY) = midpoint(t1, tr)  # Co-ordinates of midpoint between top left and top right
                (b1brX, b1brY) = midpoint(b1, br)  # Co-ordinates of midpoint between bottom left and bottom right
                (t1b1X, t1b1Y) = midpoint(t1, b1)  # Co-ordinates of mid-point between top left and bottom left
                (trbrX, trbrY) = midpoint(tr, br)  # Co-ordinates of mid-point between top right and bottom right
                # Distance between midpoints
                dA = math.sqrt(pow((trbrX-t1b1X),2) + pow((trbrY-t1b1Y),2))
                dB = math.sqrt(pow((t1trX-b1brX),2) + pow((t1trY-b1brY),2))

                pixelsPerMetric = 25
                dimA = dA / pixelsPerMetric
                dimB = dB / pixelsPerMetric
                #print("Length : ", dimA,"\nBredth : ", dimB)

                length = math.ceil(dimA)
                width = math.ceil(dimB)
                cv2.putText(orig, "{:.2f}cm".format(dimA), (int(t1trX - 15), int(t1trY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                cv2.putText(orig, "{:.2f}cm".format(dimB), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

                # show the output image
                cv2.imwrite(PATH_IMAGES+'Pic1'+'.png', orig)
                cv2.imshow("Image", orig)
                cv2.waitKey(0)
                break
        return (length,width)
