
index.js: dump.json process.py
	rm -f data/* index.js
	python3 process.py

clean:
	rm -f data/* index.js
