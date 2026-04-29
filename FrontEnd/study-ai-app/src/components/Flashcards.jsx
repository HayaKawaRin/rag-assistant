import React, { useEffect, useState } from 'react';
import Sidebar from './Sidebar';
import { Layers, Plus, Star, Trash2 } from 'lucide-react';
import {
  getFlashcardDecks,
  createFlashcardDeck,
  deleteFlashcardDeck,
  deleteFlashcardCard,
} from '../api';

const Flashcards = (props) => {
  const [showForm, setShowForm] = useState(false);
  const [deckTitle, setDeckTitle] = useState('');
  const [studyText, setStudyText] = useState('');
  const [count, setCount] = useState(5);

  const [deck, setDeck] = useState(null);
  const [decks, setDecks] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const [loading, setLoading] = useState(false);
  const [loadingDecks, setLoadingDecks] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDecks();
  }, []);

  const fetchDecks = async () => {
    try {
      setLoadingDecks(true);
      setError('');

      const data = await getFlashcardDecks();
      const savedDecks = data.decks || [];
      setDecks(savedDecks);

      if (savedDecks.length > 0) {
        setDeck(savedDecks[0]);
        setCurrentIndex(0);
        setShowAnswer(false);
      } else {
        setDeck(null);
        setCurrentIndex(0);
        setShowAnswer(false);
      }
    } catch (err) {
      setError(err.message || 'Failed to load decks.');
    } finally {
      setLoadingDecks(false);
    }
  };

  const handleCreateDeck = async () => {
    const trimmedText = studyText.trim();
    const trimmedTitle = deckTitle.trim() || 'My Flashcard Deck';

    if (!trimmedText) {
      setError('Please paste your study material first.');
      return;
    }

    setLoading(true);
    setError('');
    setShowAnswer(false);

    try {
      const data = await createFlashcardDeck({
        title: trimmedTitle,
        text: trimmedText,
        count: Number(count),
      });

      setDeck(data);
      setDecks((prev) => [data, ...prev]);
      setCurrentIndex(0);
      setShowAnswer(false);
      setShowForm(false);

      setDeckTitle('');
      setStudyText('');
      setCount(5);
    } catch (err) {
      setError(err.message || 'Failed to generate flashcards.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDeck = async (deckId) => {
    try {
      setError('');
      await deleteFlashcardDeck(deckId);

      const updatedDecks = decks.filter((item) => item.id !== deckId);
      setDecks(updatedDecks);

      if (deck?.id === deckId) {
        if (updatedDecks.length > 0) {
          setDeck(updatedDecks[0]);
        } else {
          setDeck(null);
        }
        setCurrentIndex(0);
        setShowAnswer(false);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete deck.');
    }
  };

  const handleDeleteCard = async (deckId, cardId) => {
    try {
      setError('');
      const updatedDeck = await deleteFlashcardCard(deckId, cardId);

      setDecks((prev) =>
        prev.map((item) => (item.id === deckId ? updatedDeck : item))
      );

      if (deck?.id === deckId) {
        if (updatedDeck.cards.length === 0) {
          setDeck(updatedDeck);
          setCurrentIndex(0);
          setShowAnswer(false);
        } else {
          const nextIndex =
            currentIndex >= updatedDeck.cards.length
              ? updatedDeck.cards.length - 1
              : currentIndex;

          setDeck(updatedDeck);
          setCurrentIndex(nextIndex);
          setShowAnswer(false);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to delete card.');
    }
  };

  const handleNext = () => {
    if (!deck?.cards?.length) return;
    setCurrentIndex((prev) => (prev + 1) % deck.cards.length);
    setShowAnswer(false);
  };

  const handlePrev = () => {
    if (!deck?.cards?.length) return;
    setCurrentIndex((prev) => (prev - 1 + deck.cards.length) % deck.cards.length);
    setShowAnswer(false);
  };

  const currentCard = deck?.cards?.[currentIndex];

  return (
    <div className="dashboard-layout">
      <Sidebar {...props} activeView="flashcards" />

      <main className="main-content">
        <div className="page-header-inline">
          <div
            className="tool-icon-frame"
            style={{ background: '#fce7f3', padding: '10px', borderRadius: '8px' }}
          >
            <Star color="#ec4899" size={20} />
          </div>
          <h2>Flashcard Generator</h2>
        </div>

        <p className="page-subtitle">
          Transform your study material into interactive flashcards with AI.
        </p>

        <button
          className="create-deck-btn"
          onClick={() => {
            setShowForm(!showForm);
            setError('');
          }}
        >
          <Plus size={16} />
          {showForm ? ' Close Generator' : ' Create New Deck'}
        </button>

        {showForm && (
          <div className="flashcard-generator-form">
            <div className="input-box">
              <label htmlFor="deck-title">Deck title</label>
              <input
                id="deck-title"
                type="text"
                className="flashcard-input"
                placeholder="For example: Biology Chapter 1"
                value={deckTitle}
                onChange={(e) => setDeckTitle(e.target.value)}
              />

              <label htmlFor="study-material">Study material</label>
              <textarea
                id="study-material"
                placeholder="Paste your notes, textbook passage, or study material here..."
                value={studyText}
                onChange={(e) => setStudyText(e.target.value)}
              />

              <label htmlFor="card-count">Number of cards</label>
              <select
                id="card-count"
                className="flashcard-select"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
              >
                <option value={5}>5 cards</option>
                <option value={10}>10 cards</option>
                <option value={15}>15 cards</option>
              </select>

              <div className="characters-count">{studyText.length} characters</div>

              {error && <p className="flashcard-error">{error}</p>}

              <button
                className="action-btn-pink"
                onClick={handleCreateDeck}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Flashcards'}
              </button>
            </div>
          </div>
        )}

        {!deck ? (
          <div className="empty-decks-card">
            <Layers size={44} color="#e2e8f0" />
            <p>{loadingDecks ? 'Loading decks...' : 'No flashcard decks yet'}</p>
            <p className="empty-subtitle">
              Create your first deck to start studying!
            </p>
          </div>
        ) : (
          <div className="flashcards-workspace">
            <div className="flashcards-header">
              <div>
                <h3>{deck.deck_title}</h3>
                <div className="deck-meta-row">
                  <span className="deck-language-badge">{deck.language}</span>
                  <span className="deck-count-badge">{deck.cards.length} cards</span>
                </div>
              </div>

              <span>
                {deck.cards.length > 0
                  ? `Card ${currentIndex + 1} of ${deck.cards.length}`
                  : 'No cards left'}
              </span>
            </div>

            {currentCard ? (
              <div className="flashcard-viewer">
                <div className="flashcard-main">
                  <div className="flashcard-top-row">
                    <div className="flashcard-side-label">
                      {showAnswer ? 'Answer' : 'Question'}
                    </div>

                    <button
                      className="flashcard-delete-btn"
                      onClick={() => handleDeleteCard(deck.id, currentCard.id)}
                    >
                      <Trash2 size={15} />
                      Delete Card
                    </button>
                  </div>

                  <div className="flashcard-content">
                    {showAnswer ? currentCard.answer : currentCard.question}
                  </div>

                  <button
                    className="flashcard-toggle-btn"
                    onClick={() => setShowAnswer((prev) => !prev)}
                  >
                    {showAnswer ? 'Show Question' : 'Show Answer'}
                  </button>
                </div>

                <div className="flashcard-nav">
                  <button className="flashcard-nav-btn" onClick={handlePrev}>
                    Previous
                  </button>
                  <button className="flashcard-nav-btn" onClick={handleNext}>
                    Next
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-decks-card">
                <p>No cards left in this deck</p>
              </div>
            )}

            <div className="flashcard-list">
              <h4>All cards</h4>
              {deck.cards.map((card, index) => (
                <div
                  key={card.id ?? index}
                  className={`flashcard-list-item ${index === currentIndex ? 'active' : ''}`}
                  onClick={() => {
                    setCurrentIndex(index);
                    setShowAnswer(false);
                  }}
                >
                  <strong>Q:</strong> {card.question}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="saved-decks-section">
          <div className="saved-decks-header">
            <h3>Saved decks</h3>
            <span>{decks.length} total</span>
          </div>

          {decks.length === 0 ? (
            <div className="empty-decks-card small">
              <p>No saved decks yet</p>
            </div>
          ) : (
            <div className="saved-decks-list">
              {decks.map((item) => (
                <div key={item.id} className="saved-deck-card">
                  <div
                    className="saved-deck-main"
                    onClick={() => {
                      setDeck(item);
                      setCurrentIndex(0);
                      setShowAnswer(false);
                    }}
                  >
                    <h4>{item.deck_title}</h4>
                    <div className="deck-meta-row">
                      <span className="deck-language-badge">{item.language}</span>
                      <span className="deck-count-badge">{item.cards.length} cards</span>
                    </div>
                  </div>

                  <button
                    className="saved-deck-delete-btn"
                    onClick={() => handleDeleteDeck(item.id)}
                  >
                    <Trash2 size={15} />
                    Delete Deck
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && !showForm && <p className="flashcard-error bottom-error">{error}</p>}
      </main>
    </div>
  );
};

export default Flashcards;