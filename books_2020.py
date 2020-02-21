from functools import partial
import sys


def get_libraray_value_score(libraries, ndays, l):
	lib = libraries[l]
	max_lib_score = (ndays - lib['signup_days']) * int(lib['total_book_score_submittable'] / lib['nbooks']) * lib['ship_per_day']
	return max_lib_score - (10 * lib['signup_days']) + (20 * lib['nbooks'])


def get_libraries(datafile):
	raw_data = [list(map(int, line.split())) for line in open(datafile, 'r').read().split('\n')][:-1]
	nbooks = raw_data[0][0]
	nlibraries = raw_data[0][1]
	ndays = raw_data[0][2]
	book_scores = raw_data[1]
	print(f'found books {nbooks}, libraries: {nlibraries} scanning days: {ndays}')
	libraries = []
	for i in range(nlibraries):
		nbooks = raw_data[i*2 + 2][0]
		signup_days = raw_data[i * 2 + 2][1]
		# Assert sample to show all are valid
		assert signup_days < (ndays / 2)
		ship_per_day = raw_data[i*2 + 2][2]
		book_ids = set(raw_data[i*2 + 2 + 1])
		book_batches = sorted(book_ids, reverse=True, key=lambda x: book_scores[x])
		total_books_submittable = book_batches[0: (ndays - signup_days)*ship_per_day]
		total_book_score_submittable = sum(map(lambda x: book_scores[x], total_books_submittable))
		libraries.append({
			'nbooks': nbooks,
			'signup_days': signup_days,
			'ship_per_day': ship_per_day,
			'book_ids': book_ids,
			'total_book_score_submittable': total_book_score_submittable,
			'book_batches': book_batches
		})
	return libraries, ndays, nlibraries, datafile


def generate_output(libraries, ndays, nlibraries, datafile):
	valuable_libraries = sorted(range(nlibraries), key=partial(get_libraray_value_score, libraries, ndays))
	vlidx = 0  # index for valuable libraries
	days_left = ndays
	libraries_signed_up = []
	books_collected = set()
	while days_left and vlidx < len(valuable_libraries):
		lid = valuable_libraries[vlidx]
		if libraries[lid]['signup_days'] > days_left:
			vlidx += 1
			continue
		processing_days = libraries[lid]['signup_days']
		days_left -= processing_days
		print(f'processing library {lid}, signup days: {processing_days}, days left: {days_left}')
		for slib in libraries_signed_up:
			book_batches_idx = slib['book_batches_idx']
			ship_per_day = slib['lib']['ship_per_day']
			book_batches = slib['lib']['book_batches']

			# shipped_books = book_batches[book_batches_idx: processing_days * ship_per_day]
			# books_collected.update(shipped_books)
			# book_batches_idx += processing_days * ship_per_day
			# slib['books_shipped'].extend(shipped_books)

			for _ in range(processing_days * ship_per_day):
				if book_batches_idx >= slib['lib']['nbooks']:
					break
				if not book_batches[book_batches_idx] in books_collected:
					books_collected.update([book_batches[book_batches_idx]])
					slib['books_shipped'].append(book_batches[book_batches_idx])
					book_batches_idx += 1
			slib['book_batches_idx'] = book_batches_idx
		libraries_signed_up.append({'lib': libraries[lid], 'book_batches_idx': 0, 'books_shipped': [], 'id': lid})
		vlidx += 1  # consider next library
	libraries_signed_up = list(filter(lambda x: len(x["books_shipped"]) > 0, libraries_signed_up))
	with open(f'output_{datafile}', 'w') as fd:
		fd.write(f'{len(libraries_signed_up)}')
		for library in libraries_signed_up:
			fd.write(f'\n{library["id"]} {len(library["books_shipped"])}')
			fd.write('\n' + ' '.join(map(str, library["books_shipped"])))


datafile = sys.argv[1]
generate_output(*get_libraries(datafile))

