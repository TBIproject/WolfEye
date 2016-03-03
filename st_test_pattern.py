# -*- coding: utf-8 -*-
from WolfEyes.work import *

W, H = (1280, 720)
W, H = (640, 480)

# zone minimum � analyser
# roi = (width , height)
min_palm_roi = [50, 50]

# Cr�ation de la cam�ra
cam = Camera()
cam.init(0, width=W, height=H, exposure=-4)
cam.setFOV(horizontal=math.radians(92.0))

print 'looping...'

cam.setReference(count=10)

while 1:
	# On filme
	cam.getFrame()
	
	diff = cv2.absdiff(cam.reference, cam.frame)
	diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	diff = (diff > 20).astype(np.uint8)
	
	result = (diff * 255).astype(np.uint8)
	result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
	
	# todo : utiliser des cercles plut�t que des rectangles, je pense que �a am�liorera consid�rablement la d�tection
	# probl�me actuel : plus on approche la main, plus les boucles sont lentes
	# autre probl�me : est-ce que �a d�tecte que la main ? peut-�tre rajouter des conditions...
	
	# extraction des r�gions
	# pour optimiser les fps, on utilise un pas de 10
	for y in xrange(0, diff.shape[0] - min_palm_roi[1], 10):
		for x in xrange(0, diff.shape[1] - min_palm_roi[0], 10):
			# on copie la taille minimum de la zone car elle sera modifi�e plus tard
			palm_pos = [x, y]
			palm_roi = np.copy(min_palm_roi)
			# extraction
			palm = diff[palm_pos[1]:palm_pos[1]+palm_roi[1], palm_pos[0]:palm_pos[0]+palm_roi[0]]
			# on calcule le pourcentage de pixel blanc pr�sent dans la zone
			palm_ratio = float(palm.sum()) / float(palm_roi[0] * palm_roi[1])
			
			# on regarde si la zone est bien remplie
			# l'int�r�t est de trouver la palme / le dos de la main
			if palm_ratio >= 0.9:
				
				# on �largie la zone de recherche afin de mieux englober la palme / le dos de la main
				# todo : �largir par rapport au centre du rectangle
				#        actuellement, la zone est �largie avec le point en haut � gauche
				# while palm_ratio > 0.7:
					# palm_roi[0] = palm_roi[0] + 5
					# palm_roi[1] = palm_roi[1] + 5
					# palm = diff[y:y+palm_roi[1], x:x+palm_roi[0]]
					# palm_ratio = float(palm.sum()) / float(palm_roi[0] * palm_roi[1])
					
				# on �largie par rapport au centre du rectangle
				# risque d'�tre hors index ?
				while palm_ratio >= 0.7:
					palm_roi[0] = palm_roi[0] + 5
					palm_roi[1] = palm_roi[1] + 5
					palm_pos[0] = palm_pos[0] - 5
					palm_pos[1] = palm_pos[1] - 5
					palm = diff[palm_pos[1]:palm_pos[1]+palm_roi[1], palm_pos[0]:palm_pos[0]+palm_roi[0]]
					palm_ratio = float(palm.sum()) / float(palm_roi[0] * palm_roi[1])
				#end while
				
				# zone de la main enti�re
				# on estime que la taille enti�re est le double de celle de la palme (peut-�tre � revoir)
				fingers_roi = [palm_roi[0] * 2, palm_roi[1] * 2]
				
				# extraction (pas s�r qu'il faille garder le -1)
				fingers = diff[palm_pos[1]-fingers_roi[1]/2-1:palm_pos[1]+fingers_roi[1], palm_pos[0]-fingers_roi[0]/2-1:palm_pos[0]+fingers_roi[0]]
				# on vire la zone de la palme en mettant tout � 0
				fingers[fingers_roi[1]/2-1:fingers_roi[1]/2-1+palm_roi[1], fingers_roi[0]/2-1:fingers_roi[0]/2-1+palm_roi[0]] = fingers[fingers_roi[1]/2-1:fingers_roi[1]/2-1+palm_roi[1], fingers_roi[0]/2-1:fingers_roi[0]/2-1+palm_roi[0]] * 0
				# pourcentage
				fingers_ratio = float(fingers.sum()) / float((fingers_roi[0] * fingers_roi[1]))
				
				# une main bien proportionn�e aura les doigts et une partie du bras qui occuperont environ 30% � 70% de la zone sans compter la palme
				if 0.3 <= fingers_ratio <= 0.6:
					print(fingers_ratio)
					# on trace les rectangles
					cv2.rectangle(result, (palm_pos[0], palm_pos[1]), (palm_pos[0]+palm_roi[0], palm_pos[1]+palm_roi[1]), (255, 0, 0), 2)
					cv2.rectangle(result, (palm_pos[0]-fingers_roi[0]/2-1, palm_pos[1]-fingers_roi[1]/2-1), (palm_pos[0]+fingers_roi[0], palm_pos[1]+fingers_roi[1]), (0, 255, 0), 2)
				#end if
			#end if
		#end for
	#end for
	
	# Affichage
	cv2.imshow('source', result)
	
	# Input management
	sKey = Camera.waitKey()
	if sKey == ord('q'):
		break # On quitte
		
	elif sKey == ord(' '):
		cam.setReference(count=10)
### END WHILE

# On ferme tout
Camera.closeCamApp()