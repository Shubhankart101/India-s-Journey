import VoterRollAtlas from '../components/VoterRollAtlas.jsx';
import { useDocumentTitle } from '../hooks.js';

export default function VoterRollPage() {
  useDocumentTitle('SIR, SSR and your voter roll');
  return <VoterRollAtlas />;
}
