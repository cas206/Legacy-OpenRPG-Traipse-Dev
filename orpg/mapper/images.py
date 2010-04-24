# Copyright (C) 2000-2001 The OpenRPG Project
#
#    openrpg-dev@lists.sourceforge.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# --
#
# File: mapper/images.py
# Author: OpenRPG
# Maintainer:
# Version:
#   $Id: images.py,v Traipse 'Ornery-Orc' prof.ebral Exp $
#
# Description:
#
from __future__ import with_statement

import urllib, Queue, thread, time
from threading import Lock
from orpg.orpg_wx import *
from orpg.orpgCore import *

from orpg.dirpath import dir_struct
from orpg.tools.orpg_log import logger
from orpg.tools.settings import settings

class ImageHandlerClass(object):
    __cache = {}
    __fetching = {}
    __queue = Queue.Queue(0)
    __lock = Lock()

    def __new__(cls):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        return it

    def load(self, path, image_type, imageId):
        # Load an image, with a intermideary fetching image shown while it loads in a background thread
        if self.__cache.has_key(path):
            return wx.ImageFromMime(self.__cache[path][1],
                                    self.__cache[path][2])
        if path not in self.__fetching:
            self.__fetching[path] = True
            #Start Image Loading Thread
            thread.start_new_thread(self.__loadThread,
                                    (path, image_type, imageId))
        else:
            if self.__fetching[path]:
                thread.start_new_thread(self.__loadCacheThread,
                                        (path, image_type, imageId))
        return wx.Image(dir_struct["icon"] + "fetching.png", wx.BITMAP_TYPE_PNG)

    def directLoad(self, path):
        # Directly load an image, no threads
        if path in self.__cache:
            return wx.ImageFromMime(self.__cache[path][1],
                                    self.__cache[path][2])
        uriPath = urllib.unquote(path)
        try:
            d = urllib.urlretrieve(uriPath)
            # We have to make sure that not only did we fetch something, but that
            # it was an image that we got back.
            if d[0] and d[1].getmaintype() == "image":
                with self.__lock:
                    self.__cache[path] = (path, d[0], d[1].gettype(), None)
                return wx.ImageFromMime(self.__cache[path][1], self.__cache[path][2])
            else:
                logger.general("Image refused to load or URI did not "
                               "reference a valid image: " + path, True)
                return None
        except IOError:
            logger.general("Unable to resolve/open the specified URI; "
                           "image was NOT loaded: " + path, True)
            return None

    def cleanCache(self):
        # Shrinks the Cache down to the proper size
        try:
            cacheSize = int(settings.get("ImageCacheSize"))
        except:
            cacheSize = 32
        cache = self.__cache.keys()
        cache.sort()
        for key in cache[cacheSize:]:
            del self.__cache[key]

    def flushCache(self):
        # This function will flush all images contained within the image cache.
        with self.__lock:
            self.__cache = {}
            self.__fetching = {}
            urllib.urlcleanup()

    #Private Methods
    def __loadThread(self, path, image_type, imageId):
        uriPath = urllib.unquote(path)
        try:
            d = urllib.urlretrieve(uriPath)
            # We have to make sure that not only did we fetch something, but that
            # it was an image that we got back.
            if d[0] and d[1].getmaintype() == "image":
                with self.__lock:
                    self.__cache[path] = (path, d[0], d[1].gettype(), imageId)
                    self.__queue.put((self.__cache[path], image_type, imageId))
                if path in self.__fetching: del self.__fetching[path]
            else:
                logger.general("Image refused to load or URI did not "
                               "reference a valid image: " + path, True)
                self.__queue.put(('failed', image_type, imageId))
                del self.__fetching[path]
        except IOError:
            del self.__fetching[path]
            logger.general("Unable to resolve/open the specified URI; "
                           "image was NOT laoded: " + path, True)
            self.__queue.put((dir_struct["icon"] + "failed.png", image_type, imageId))

    def __loadCacheThread(self, path, image_type, imageId):
        try:
            st = time.time()
            while path in self.__fetching and self.__fetching[path] is not False:
                time.sleep(0.025)
                if (time.time()-st) > 120:
                    logger.general("Timeout: " + path, True)
                    del self.__fetching[path]
                    break
        except:
            del self.__fetching[path]
            logger.general("Unable to resolve/open the specified URI; "
                           "image was NOT loaded: " + path, True)
            return
        with self.__lock:
            if path in self.__cache:
                logger.debug("Adding Image to Queue from Cache: " + str(self.__cache[path]))
                self.__queue.put((self.__cache[path], image_type, imageId))
            else: self.__loadThread(path, image_type, imageId)

    #Property Methods
    def _getCache(self):
        return self.__cache

    def _getQueue(self):
        return self.__queue

    #Properties
    Cache = property(_getCache)
    Queue = property(_getQueue)

ImageHandler = ImageHandlerClass()
