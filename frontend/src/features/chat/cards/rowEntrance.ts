/** A card's rows follow it 40 ms apart, 200 ms each; under reduced motion they don't stagger. */
export function rowEntrance(index: number) {
  return {
    className: 'motion-safe:animate-message-in',
    style: { animationDelay: `${index * 40}ms` },
  };
}
