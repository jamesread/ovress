function newP(text) {
	return $('<p />').text(text)
}

function newContentJson(url, callback) {
	newContent();
	$.getJSON(url, resListRoots)
}

function reqListRoots() {
	newContentJson('/listRoots', resListRoots)
}

function promptRegisterRoot() {
	root = window.prompt("path?");

	$.getJSON("/registerRoot?path=" + root);
}

function resListRoots(json) {
	content = newContent();
	console.log(json)

	tbl = $('<table><thead><tr /></thead><tbody /></table>');
	thead = tbl.find('tr')
	thead.append('<th>Root</th><th>Peers</th><th>Actions</th><th>Status</th>');
	tbody = tbl.find('tbody');

	$(json.roots).each(function(index, root) {
		row = $('<tr><td>Local path: ' + root.path + '</td><td class = "peers">-</td><td class = "actions" /><td class = "status">' + root.status + '</td></tr>')
		peersCell = row.find('td.peers')
		
		$(root.peers).each(function(peerIndex, peer) {
			peersCell.append('<p>peer: ' + peer.id + '</p>')
		});

		actionsCell = row.find('td.actions')
		actionsCell.append($('<a />').text("X").attr('href', 'removeRoot?path=' + root.path))
		actionsCell.append($('<a />').text("Rescan").attr('href', 'rescan?path=' + root.path))
		actionsCell.append($('<a />').text("Stop").attr('href', 'stopRescan?path=' + root.path))
		actionsCell.append($('<a />').text("Contents").attr('href', 'listRootContents?path=' + root.path))
		tbody.append(row)
	});

	content.append(tbl)

	newP(json.roots.length + ' roots in total.').appendTo(content)
}

function newContent() {
	$('content').children().remove();

	return $('content');
}

function Header() {
	var self = this;

	dom = $('<header/>').appendTo('body');
	linkListRoots = $('<a id = "listRoots" href = "#listRoots">Roots</a>').click(reqListRoots).appendTo(dom);
	linkRegisterRoot = $('<a id = "registerRoot" href = "#registerRoot">Register</a>').click(promptRegisterRoot).appendTo(dom);

	return self;
}

function reqRefreshStatus() {
	$.getJSON("/status", null, resRefreshStatus);
}

function resRefreshStatus(json) {
	if (json.rootCount == 0) {
		$('a#listRoots').addClass('disabled')
	} else {
		$('a#listRoots').removeClass('disabled')
	}
}

function init() {
	window.header = new Header();

	$('<content />').appendTo('body');
}

function loadUrlHash() {
	switch(window.location.hash) {
		case '#listRoots':
			reqListRoots()
			break
	}
}

$(document).ready(function() {
	init();	

	reqRefreshStatus();
	loadUrlHash();
});
