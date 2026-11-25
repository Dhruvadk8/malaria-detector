import React, { useState } from 'react';
import { Star, Heart, Send } from 'lucide-react';
import { sendCSAT } from '../../services/api';

interface CSATModalProps {
  conversationId: string;
  onClose: () => void;
}

export const CSATModal: React.FC<CSATModalProps> = ({ conversationId, onClose }) => {
  const [rating, setRating] = useState<number>(5);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    await sendCSAT(conversationId, rating, comment);
    setSubmitted(true);
    setTimeout(() => {
      onClose();
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 text-center shadow-2xl">
        
        {!submitted ? (
          <>
            <div className="w-12 h-12 bg-indigo-500/10 text-indigo-400 rounded-full flex items-center justify-center mx-auto mb-3">
              <Heart className="w-6 h-6 fill-indigo-500/20" />
            </div>

            <h3 className="text-xl font-bold text-white mb-1">How was your experience?</h3>
            <p className="text-xs text-slate-400 mb-5">
              Help us improve SupportAI by rating your conversation quality.
            </p>

            {/* Star Rating */}
            <div className="flex items-center justify-center space-x-2 mb-6">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => setRating(star)}
                  className="p-1.5 focus:outline-none transition transform hover:scale-110"
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= (hoverRating || rating)
                        ? 'text-amber-400 fill-amber-400'
                        : 'text-slate-700'
                    }`}
                  />
                </button>
              ))}
            </div>

            <textarea
              rows={3}
              placeholder="Tell us what worked well or what we can improve..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500 mb-5"
            />

            <div className="flex items-center justify-end space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-slate-800 text-slate-400 hover:text-white text-sm font-medium rounded-xl transition"
              >
                Skip
              </button>
              <button
                onClick={handleSubmit}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition flex items-center space-x-2 shadow-lg shadow-indigo-600/20"
              >
                <Send className="w-4 h-4" />
                <span>Submit Feedback</span>
              </button>
            </div>
          </>
        ) : (
          <div className="py-6 space-y-3">
            <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-full flex items-center justify-center mx-auto">
              <Heart className="w-6 h-6 fill-emerald-500" />
            </div>
            <h4 className="text-lg font-bold text-white">Thank You!</h4>
            <p className="text-xs text-slate-400">Your feedback has been saved.</p>
          </div>
        )}

      </div>
    </div>
  );
};
