import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import './Home.css'

function Home() {
  const [boards, setBoards] = useState([])
  const [filteredBoards, setFilteredBoards] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)

  const loadBoardStats = async () => {
    try {
      const remoteBoards = await api.getBoards()
      const stats = await Promise.all(remoteBoards.map(async (board) => {
        try {
          const posts = await api.getPosts(board.id)
          return {
            ...board,
            postCount: posts?.length || 0,
          }
        } catch (error) {
          console.error(`Error loading stats for board ${board.id}:`, error)
          return {
            ...board,
            postCount: 0,
          }
        }
      }))
      setBoards(stats)
    } catch (error) {
      console.error('Error loading board stats:', error)
      setBoards([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Load post counts for each board
    loadBoardStats()

    // Refresh stats when window regains focus (user navigates back)
    const handleFocus = () => {
      loadBoardStats()
    }
    window.addEventListener('focus', handleFocus)

    return () => {
      window.removeEventListener('focus', handleFocus)
    }
  }, [])

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredBoards(boards)
    } else {
      const query = searchQuery.toLowerCase()
      const filtered = boards.filter(
        board =>
          board.name.toLowerCase().includes(query) ||
          board.description.toLowerCase().includes(query)
      )
      setFilteredBoards(filtered)
    }
  }, [searchQuery, boards])

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading boards...</p>
      </div>
    )
  }

  return (
    <div className="home">
      <div className="home-intro">
        <h2>Welcome to LEN!</h2>
      </div>

      <div className="search-container">
        <input
          type="text"
          placeholder="Search communities..."
          className="search-input"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="section-separator"></div>

      {searchQuery && filteredBoards.length === 0 && boards.length > 0 && (
        <div className="search-results-message">
          <p>No communities found matching "{searchQuery}"</p>
        </div>
      )}

      <div className="boards-grid">
        {filteredBoards.map((board) => (
          <Link key={board.id} to={`/board/${board.id}`} className="board-card">
            <h3>{board.name}</h3>
            <p className="board-description">{board.description}</p>
            <div className="board-meta">
              <span className="post-count">{board.postCount} {board.postCount === 1 ? 'post' : 'posts'}</span>
            </div>
          </Link>
        ))}
      </div>

      {boards.length === 0 && (
        <div className="empty-state">
          <p>No boards available at the moment.</p>
        </div>
      )}
    </div>
  )
}

export default Home
