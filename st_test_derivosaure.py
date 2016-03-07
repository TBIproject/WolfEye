# -*- coding: utf-8 -*-
from WolfEyes.work import *

W, H = (1280, 720)
W, H = (640, 480)

blockSize = pyon(
	width = 5,
	height = 5,
)

spread = 20

# Cr�ation de la cam�ra
cam = Camera()
cam.init(0, width=W, height=H, exposure=-4)
cam.setFOV(horizontal=math.radians(92.0))
cam.setImageVertBand(0.45, 0.55)

cam.setReference(count=10)
ref_deriv = cf.Scharr(cam.reference)

print 'looping...'

while 1:
	cam.getFrame()
	corrected_frame = cam.reference.copy()
	deriv = cf.Scharr(cam.frame)
	deriv = cv2.dilate(deriv, (9, 9))
	
	for y in xrange(0, deriv.shape[0], blockSize.height):
		filling = False
		can_close = True
		for x in xrange(0, deriv.shape[1], blockSize.width):
			ref_deriv_part = ref_deriv[y:y+blockSize.height, x:x+blockSize.width]
			deriv_part = deriv[y:y+blockSize.height, x:x+blockSize.width]
			
			deriv_diff = abs(int(ref_deriv_part.sum()) - int(deriv_part.sum())) / float(blockSize.width * blockSize.height * 3 * 255)
			
			if deriv_diff >= 0.025:
				corrected_frame[y-spread:y+blockSize.height+spread, x-spread:x+blockSize.width+spread] = cam.frame[y-spread:y+blockSize.height+spread, x-spread:x+blockSize.width+spread]

				# if can_close:
					# filling = not filling
					# can_close = False
			# else:
				# can_close = True
				
			# if filling:
				# corrected_frame[y-spread:y+blockSize.height+spread, x-spread:x+blockSize.width+spread] = cam.frame[y-spread:y+blockSize.height+spread, x-spread:x+blockSize.width+spread]
			# end if
		# end if
	# end for
	
	diff = cv2.absdiff(corrected_frame, cam.reference)
	diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	diff = ((diff > 20) * 255).astype(np.uint8)
	
	cam._BINARY = diff.copy();
	
	cam.arounder(
		maxCount=1000,
		minArea=64,
		maxDist=1,
		thick=1
	)
	
	cv2.imshow('frame', cam.frame)
	cv2.imshow('deriv', deriv)
	cv2.imshow('corrected_frame', corrected_frame)
	cv2.imshow('diff', diff)
	cv2.imshow('stream', cam.stream)
	
	# Input management
	sKey = Camera.waitKey()
	if sKey == ord('q'):
		break # On quitte
	
### END WHILE

# On ferme tout
Camera.closeCamApp()