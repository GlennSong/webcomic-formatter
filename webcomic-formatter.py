import json     #load json data
import sys      #command line arguments
import os       #make directory
import math
import time
from PIL import Image, UnidentifiedImageError
from datetime import datetime, UTC


#function definitions
def showHelp():
    print ("\n\nWebcomic Formatter Tool Help")
    print ("\nCommand line syntax: webcomic-formatter.py <parent-folder-name>")
    print ("\n\n")

def IsThumbnail(imageFilePath):
    if(isinstance(imageFilePath, str)
        and (imageFilePath.endswith(".png") or (imageFilePath.endswith(".jpg")))
        and imageFilePath.find("thumb") != -1):
        return True
    else: 
        return False

def IsSocialMediaCard(imageFilePath):
    if(isinstance(imageFilePath, str)
        and imageFilePath.endswith(".png") 
        and imageFilePath.find("social") != -1):
        return True
    else: 
        return False

def IsImage(imageFilePath):
    if(isinstance(imageFilePath, str)
        and imageFilePath.endswith(".png")) or (imageFilePath.endswith(".jpg")):
        return True
    else: 
        return False

def IsTextFile(filePath):
    if(isinstance(filePath, str)
        and filePath.endswith(".txt")):
        return True
    else: 
        return False

def VerticalStitchImages(imageFileList): 
    
    maxW = 0
    maxH = 0
    Images = []
    
    parentDirAndFile = imageFileList[0].rsplit('\\', 1)
    FileAndExt = os.path.splitext(parentDirAndFile[1])
    newImageFilePath = parentDirAndFile[0] + "\\"
#    newImageFilePath += "\\" + configItem["output-suffix"] + "\\" 

    for imageFile in imageFileList:
        data = Image.open(imageFile)
        (w, h) = data.size
        
        if(w >= maxW) : 
            maxW = w

        maxH += h
        Images.append(data)

    vertImage = Image.new('RGB', (maxW, maxH))
    currH = 0
    for imageFile in imageFileList :
        data = Image.open(imageFile)
        (imgW, imgH) = data.size
        vertImage.paste(im = data, box=(0,currH))
        currH += imgH

    filePath = newImageFilePath + "vert-" + configItem["output-suffix"] + FileAndExt[1]
    vertImage.save(filePath)
    print("Single Vertical Image saved at {}".format(filePath))

def ProcessImage(configItem, imagePath):
    imgPathList = []
    # img = Image.open(imagePath)
    if imagePath.startswith("._"):
        print(f"Skipping hidden file: {imagePath}")
        return None

    try: 
        with Image.open(imagePath) as img : 
            parentDirAndFile = os.path.split(imagePath)
            FileAndExt = os.path.splitext(parentDirAndFile[1])
            newImageFilePath = parentDirAndFile[0] 
            newImageFilePath = os.path.join(newImageFilePath, configItem["output-suffix"])

            resizeW = configItem["max-width"]
            resizeH = configItem["max-height"]

            #resize image
            baseW = img.size[0]
            p = resizeW/float(baseW)
            resizedImg = img.resize((resizeW,math.ceil(img.size[1] * p)), Image.Resampling.LANCZOS)

            #if the resized image height is less than the tile height, save the file out as-is
            if resizedImg.size[1] <= resizeH: 
                noResizeImgPath = os.path.join(newImageFilePath, FileAndExt[0] + "-" + configItem["output-suffix"] + FileAndExt[1])

                resizedImg.save(noResizeImgPath)
                print("Image saved at {}".format(noResizeImgPath))
                imgPathList.append(noResizeImgPath)
                return imgPathList

            #cut the image into tiles.
            newImgH = resizedImg.size[1]
            splitImgCnt = math.floor(newImgH/resizeH)
            imgCnt = 0
            for i in range(0, resizeH * splitImgCnt, resizeH):
                box = (0, i, resizeW, i+resizeH)
                imgTile = resizedImg.crop(box)
                
                imgTilePath = os.path.join(newImageFilePath, FileAndExt[0] + "-" + configItem["output-suffix"] + f"{imgCnt:02}" + FileAndExt[1])

                imgTile.save(imgTilePath)
                print("Image Tile saved at {}".format(imgTilePath))
                imgPathList.append(imgTilePath)
                imgCnt += 1

            #calculate any remainder
            remainderH = newImgH - (splitImgCnt * resizeH)
            if(remainderH > 0):
                remainderBox = (0, resizeH * splitImgCnt, resizeW, resizeH * splitImgCnt + remainderH)
                remainderImgTile = resizedImg.crop(remainderBox)
                
                remainderImgTilePath = os.path.join(newImageFilePath, FileAndExt[0] + "-" + configItem["output-suffix"] + f"{imgCnt:02}" + FileAndExt[1])

                remainderImgTile.save(remainderImgTilePath)
                imgPathList.append(remainderImgTilePath)
                print("Image Tile saved at {}".format(remainderImgTilePath))
    except UnidentifiedImageError:
        print(f"Error: Cannot identify image file {imagePath}")

    return imgPathList

def ProcessThumbnail(configItem, thumbnailPath): 
    if thumbnailPath.startswith("._"):
        print(f"Skipping hidden file: {thumbnailPath}")
        return None

    try:
        # img = Image.open(thumbnailPath)
        with Image.open(thumbnailPath) as img: 

            #split at the end to remove the file name.
            parentDirAndFile = os.path.split(thumbnailPath)

            FileAndExt = os.path.splitext(parentDirAndFile[1])
            newThumbFilePath = parentDirAndFile[0] 
            newThumbFilePath = os.path.join(newThumbFilePath, configItem["output-suffix"])

            newThumbFilePath = os.path.join(newThumbFilePath, FileAndExt[0] + "-" + configItem["output-suffix"] + FileAndExt[1])

            thumbW = configItem["thumb-width"]
            thumbH = configItem["thumb-height"]
            maxDim = max(thumbW, thumbH)
            minDim = min(thumbW, thumbH)
            newImg = img.resize((maxDim, maxDim), Image.Resampling.LANCZOS)
            
            offsetA = math.ceil((maxDim - minDim) * 0.5)
            offsetB = (maxDim - minDim) - offsetA
            if(minDim == thumbW): 
                top = 0
                left = offsetA
                right = maxDim  - offsetB
                bottom = maxDim
            elif(minDim == thumbH):
                top = offsetA
                left = 0
                right = maxDim
                bottom = maxDim - offsetB

            croppedNewImg = newImg.crop((left, top, right, bottom))
            croppedNewImg.save(newThumbFilePath)
            print("Created thumbnail: {} at size {}x{}".format(newThumbFilePath, croppedNewImg.width, croppedNewImg.height))
            return newThumbFilePath
    except UnidentifiedImageError:
        print(f"Error: Cannot identify image file {thumbnailPath}")

def ProcessSocialMediaCard(configItem, path) : 
    if path.startswith("._"):
        print(f"Skipping hidden file: {path}")
        return None

    try: 
        with Image.open(path) as img:
            #split at the end to remove the file name.
            parentDirAndFile = os.path.split(path)

            FileAndExt = os.path.splitext(parentDirAndFile[1])
            newPath = parentDirAndFile[0] 
            newPath = os.path.join(newPath, configItem["output-suffix"])

            newPath = os.path.join(newPath, FileAndExt[0] + "-" + configItem["output-suffix"] + FileAndExt[1])

            newImg = img.copy()
            newImg.save(newPath)
            print("Copied social media card:{}".format(newPath))
            return newPath
    except UnidentifiedImageError:
        print(f"Error: Cannot identify image file {path}")

def CreatePost(configItem, textPath):
    output = ""
    #read the file contents and append to the markdown header info
    with open(textPath, errors='backslashreplace') as postFile:
        lines = postFile.readlines()
        if lines:
            for line in lines:
                newline = line.rstrip() + "\n\r"
                output += newline
        else: 
            output += "<post text goes here>\n"

    parentDirAndFile = os.path.split(textPath)

    FileAndExt = os.path.splitext(parentDirAndFile[1])
    newFilePath = parentDirAndFile[0] 
    newFilePath = os.path.join(newFilePath, configItem["output-suffix"])

    newFilePath = os.path.join(newFilePath, FileAndExt[0] + "-" + configItem["output-suffix"] + FileAndExt[1])

    #write out the markdown header.
    with open(newFilePath, 'w') as file : 
        file.write(output)

# This is specific for the gatsby webcomic site template.
def CreateSiteMarkdown(configItem, textPath, socMediaName, thumbName, imageList):
    if os.path.basename(textPath).startswith("._"):
        print(f"Skipping hidden file: {textPath}")
        return None

    print(imageList)
    
    args = {
        "title" : "\"Untitled Comic\"",
        "slug" : "\"create-slug-here\"",
        "date" : "\"" + datetime.now(UTC).isoformat(timespec='microseconds').replace("+00:00", "") + "Z\"",
        "posttype" : "\"comicpage\"",
        "comic" : "\"<comicFolderName>\"",
        "chapter" : "\"<chapterName>\""
    }

    output = '''---
title: {title}
slug: {slug}
date: {date}
posttype: {posttype}
comic: {comic}
chapter: {chapter}
'''.format(**args)

    if thumbName: 
        thumbDirAndFile = os.path.split(thumbName)

        output += "thumbnailImage: \"" + thumbDirAndFile[1] + "\""

    if socMediaName: 
        socMediaDirAndFile = os.path.split(socMediaName)
        
        output += "\nsocialMediaImage: \"" + socMediaDirAndFile[1] + "\""

    if len(imageList) > 1: 
        output += "\ncomicImageStack:\n" 
        for imageName in imageList: 
            imgDirAndFile = os.path.split(imageName)

            output += " - \"" + imgDirAndFile[1] + "\"\n"
    else : 
        imgDirAndFile = os.path.split(imageList[0])

        output += "\ncomicImage: \"" + imgDirAndFile[1] + "\"\n"

    output += "---\n" #end header

    try:
        print(f"filename is {textPath}")
        with open(textPath, "r", encoding="utf-8", errors="replace") as postFile:
            lines = postFile.readlines()
            if lines:
                for line in lines:
                    # Handle any weird line endings
                    newline = line.rstrip("\r\n") + "\n"
                    output += newline
            else:
                output += "<post text goes here>\n"
    except FileNotFoundError:
        print(f"Error: File not found at {textPath}")
    except Exception as e:
        print(f"Error: {e}")

    # #read the file contents and append to the markdown header info
    # with open(textPath, errors='backslashreplace') as postFile:
    #     lines = postFile.readlines()
    #     if lines:
    #         for line in lines:
    #             newline = line.rstrip() + "\n"
    #             output += newline
    #     else: 
    #         output += "<post text goes here>\n"

    #write out the markdown header.
    #parentDirAndFile = textPath.rsplit('\\', 1)
    parentDirAndFile = os.path.split(textPath)

    FileAndExt = os.path.splitext(parentDirAndFile[1])
    newFilePath = parentDirAndFile[0] 
    newFilePath = os.path.join(newFilePath, configItem["output-suffix"])
    #print("New file path:", newFilePath)

    newFilePath = os.path.join(newFilePath, "index.md")

    with open(newFilePath, 'w') as file : 
        file.write(output)
#Main

# Get command line arguments
#arg 0: running python script name
#arg 1: parent folder path

numArgs = len(sys.argv)
parentPath = '';
if(numArgs > 1): 
    # print("\nFirst arg:", sys.argv[1])

    parentPath = sys.argv[1]
    
    if(not os.path.exists(parentPath)): 
        print("Parent directory {} doesn't exist!".format(parentPath))
        showHelp()
        exit()

    if(not os.path.isdir(parentPath)):
        print("Did not enter a valid path! (user entered: {})".format(parentPath))
        showHelp()
        exit()
        
    #check if the argument is a valid directory
else:
    showHelp()
    exit()

# TODO: detect if that folder exists

startTime = time.time()

#read the config file for the different webcomic formats.
configData = {}
with open("config.json") as configFile : 
    configData = json.load(configFile)

if not configData: 
    print("ERROR: Could not load config data! Make sure you have the right file name and path!")
    exit()

# be able to read the files from the input directory
dirFiles = os.listdir(parentPath)

for configItem in configData["formats"]:
    postFilePath = ""
    thumbReturnValue = ""
    socMediaReturnValue = ""
    imgListReturnValue = []

    # decide if we want to process the configuration
    if not configItem["will-process-flag"]: 
        continue

    #create a new subfolder
    newOutputPath = os.path.join(parentPath, configItem["output-suffix"])
    if(not os.path.exists(newOutputPath)):
        os.mkdir(newOutputPath)
        print("{} folder created!".format(configItem["output-suffix"]))
    else: 
        print("{} already exists, overwriting data in folder".format(configItem["output-suffix"]))

    #process the files
    for filePathStr in dirFiles : 
        if filePathStr.startswith("._"):
            print(f"Skipping hidden file: {filePathStr}")
            continue

        fileData = os.path.splitext(filePathStr)
        fullPath = os.path.join(parentPath, filePathStr)
        if(IsThumbnail(fullPath)): 
            thumbReturnValue = ProcessThumbnail(configItem, fullPath)
        elif(configItem["include-soc-media-flag"] and IsSocialMediaCard(fullPath)):
            socMediaReturnValue = ProcessSocialMediaCard(configItem, fullPath)
        elif(IsImage(fullPath)):
            tempList = ProcessImage(configItem, fullPath)
            for tempImgName in tempList: 
                imgListReturnValue.append(tempImgName)
        elif(IsTextFile(fullPath)):
            postFilePath = fullPath

    # do we need to create a single vertical image?
    if configItem["build-vertical-image"]: 
        VerticalStitchImages(imgListReturnValue)

    #process the post info last.    
    if postFilePath: 
        if configItem["process-as-md"]:
            CreateSiteMarkdown(configItem, postFilePath, socMediaReturnValue, thumbReturnValue, imgListReturnValue)
        else:
            CreatePost(configItem, postFilePath)                

    print("Processed images and post for {}, output dir: {}\n".format(configItem["output-suffix"], newOutputPath))

timeLapsed = time.time() - startTime
print("Job completed and took {} seconds".format(timeLapsed))
