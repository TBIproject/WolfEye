# -*- coding: utf-8 -*-*
"""Tools for everyday tasks"""
from D2Point import *
import numpy as np
import cv2
import sys

# PRINTF!!
def printf(txt):
	"""No line feed at the end ! :D"""
	sys.stdout.write(txt)

# Dimensions d'une matrice (image)
def height(img):
	"""Get an image's height"""
	return np.shape(img)[0]
	
def width(img):
	"""Get an image's width"""
	return np.shape(img)[1]
	
def channels(img):
	"""List an image's channels"""
	shape = np.shape(img)
	return shape[2] if len(shape) > 2 else 1

# Constrain
def constrain(min, max, *args):
	"""Constrain a value between min and max
	 syntax: constrain(min, max, value1, value2, value3, ...)
	         constrain(min, max, *arglist)"""
	result = []
	for n in args: result.append(min if n < min else max if n > max else n)
	if len(args) == 1: return result[0]
	else: return tuple(result)
	
# Image vide (easypeasy)
def Empty(**kargs):
	"""Creates an empty image from some inputs:
	 - channels: number of channels (3)
	 - height (1)
	 - width (1)"""
	channels = kargs.get('channels', 3)
	height = kargs.get('height', 1)
	width = kargs.get('width', 1)
	return np.zeros((height, width, channels), np.uint8) if channels > 1 else np.zeros((height, width), np.uint8)
	
# Image vide depuis une autre image
def EmptyFrom(img, chan=None):
	"""Creates an empty image from another (same size, uint8)"""
	if not chan: chan = channels(img)
	return Empty(height=height(img), width=width(img), channels=chan)
	
# Retourne la liste des maximums d'un contour
def limiter(contour, maxDist=0):
	"""Returns every extrem-bottom points from a contour"""
	cnt = contour.copy()
	initial = start = end = None
	
	for _ in xrange(len(cnt)):
		i = cnt[:,:,1].argmax()
		point = D2Point(cnt[i][0][0], cnt[i][0][1])
		
		# Si c'est le premier point
		if not initial:
			initial = start = end = point
		
		# Les suivants
		elif point.y >= (initial.y - maxDist):
		
			# Découpage
			if  point.x >= initial.x: end = point
			elif point.x < initial.x: start = point
		
		# Si on a fini
		else: break
		
		# On balade le point
		cnt[i][0] = [-1, -1]
	###
	
	# Résultat
	result = (start % end)
	result.y = initial.y
	
	return result

# _Anti _NOISE _Kernel
def anoisek(r=5, debug=False):
	"""Function to create a kernel for anti-noise purposes"""
	
	w, h = 2*r+1, 2*r+1
	kernel = np.zeros((w, h), np.float32)
	
	if debug: print
	for u in xrange(w):
		x = r - u
		
		for v in xrange(h):
			y = r - v
			
			dist = (x**2 + y**2) ** 0.5
			val = dist/r
			
			if dist <= r:
				kernel.itemset((u, v), val)
				if debug: printf('#')
			elif debug: printf(' ')
		###
		if debug: printf('\n ')
	###
	
	kernel /= kernel.sum()
	return kernel	

# Création d'une image à partir d'un histogramme
def histogram(img, gamma=0.3):
	"""Creates an image's histogram to display"""
	
	shape = img.shape
	cans = shape[2] if len(shape) > 2 else 1
	result = np.zeros((256, 256, cans), np.uint8)
	max = height(img) * width(img)
	
	# Si l'image possède plusieurs cannaux
	for i in range(cans):
		
		# On calcule
		hist = cv2.calcHist([img], [i], None, [256], [0, 256])
		values = (255 * (hist / max)**gamma).astype(np.uint8)[:]
		
		# On affiche
		for j in xrange(len(values)):
			result[:values[j], j, i] = 255
	
	# RETURN
	return result
	
# Essaye de supprimer le décalage absolu
def grounder(img):
	"""Tries to remove absolute offset
	'img' must be a 3 colors image"""
	shape = img.shape
	
	# Mise en forme
	a = img.reshape((shape[0] * shape[1], 3))
	min = np.zeros(a.shape)
	max = np.zeros(a.shape)
	
	# Minimas/maximas
	min[:,0] = min[:,1] = min[:,2] = a.min(axis=1)
	max[:,0] = max[:,1] = max[:,2] = a.max(axis=1)
	
	# Remise en forme
	min = min.reshape(shape)
	max = max.reshape(shape)
	
	# Remise au ras du sol
	grounded = img - min
	
	# return (grounded / max).astype(np.float32)
	return (grounded / 255.0).astype(np.float32)
	
# Objet pour retourner des trucs
class Statos:
	"""Gets a flow of image and creates some stats"""
	
	# Init <3
	def __init__(this, **kargs):
		this.count = kargs.get('count', 10)
	
	def reset(this):
		this.__i = 0
		this.mean = None
		this.var = None
	
	@property
	def count(this): return this.__count
	
	@count.setter
	def count(this, value):
		this.reset()
		return this.__count = 0 if value < 0 else value
	
	# Miam
	def feed(this, img):
		if this.mean is None:
			this.mean = np.zeros(img.shape), np.uint32)
		if this.var is None:
			this.var = np.zeros(img.shape, np.uint8)
		
		this.mean += img