var board = null
var game = new Chess()

function onDragStart (source, piece) {
  if (game.game_over()) return false
}

function onDrop (source, target) {
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q'
  })

  if (move === null) return 'snapback'
}

function onSnapEnd () {
  board.position(game.fen())
}

board = Chessboard('board', {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd
})