import React from 'react';
import { ArrowRight } from 'lucide-react';

const ToolCard = ({ icon, title, desc }) => (
  <div className="tool-card">
    <div className="tool-icon">{icon}</div>
    <h3>{title}</h3>
    <p>{desc}</p>
    <div className="open-link">Open <ArrowRight size={14} /></div>
  </div>
);

export default ToolCard;